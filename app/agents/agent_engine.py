from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.core.config import AGENT_MAX_ACTIONS_PER_EVENT, AGENT_REQUIRE_APPROVAL_FOR_CRITICAL
from app.integrations.webhook_dispatcher import dispatch_webhook
from app.models.ai_agent_action import AIAgentAction
from app.schemas.ticket_schema import TicketCreate
from app.schemas.work_order_schema import WorkOrderCreate
from app.services.ticket_service import create_ticket
from app.services.work_order_service import create_work_order

logger = logging.getLogger(__name__)

CRITICAL_ACTIONS = {"create_ticket", "create_work_order", "trigger_webhook"}


@dataclass
class AgentEvent:
    event_type: str
    payload: dict
    context: dict


class BaseAgent(ABC):
    name: str
    events_subscribed: list[str]

    @abstractmethod
    def evaluate(self, event: AgentEvent) -> dict:
        pass

    @abstractmethod
    def execute(self, db: Session, actions: list[dict]) -> list[dict]:
        pass


class AgentActionExecutor:
    @staticmethod
    def enforce_safety(event_payload: dict, actions: list[dict]) -> tuple[list[dict], list[str]]:
        warnings: list[str] = []
        limited_actions = actions[:AGENT_MAX_ACTIONS_PER_EVENT]

        if len(actions) > AGENT_MAX_ACTIONS_PER_EVENT:
            warnings.append("Max actions per event reached; extra actions were dropped")

        if AGENT_REQUIRE_APPROVAL_FOR_CRITICAL and not bool(event_payload.get("approved", False)):
            filtered: list[dict] = []
            for action in limited_actions:
                action_type = action.get("type")
                if action_type in CRITICAL_ACTIONS:
                    warnings.append(f"Action '{action_type}' requires explicit approval")
                    continue
                filtered.append(action)
            limited_actions = filtered

        return limited_actions, warnings

    @staticmethod
    def execute_action(db: Session, action: dict) -> dict:
        action_type = action.get("type")

        if action_type == "create_ticket":
            payload = action.get("payload", {})
            ticket = create_ticket(
                db=db,
                payload=TicketCreate(
                    title=payload["title"],
                    description=payload.get("description"),
                    customer_id=payload["customer_id"],
                    priority=payload.get("priority", "MEDIUM"),
                ),
            )
            return {"type": action_type, "status": "SUCCESS", "ticket_id": ticket.id}

        if action_type == "create_work_order":
            payload = action.get("payload", {})
            work_order = create_work_order(
                db=db,
                payload=WorkOrderCreate(
                    ticket_id=payload["ticket_id"],
                    assigned_user_id=payload["assigned_user_id"],
                ),
            )
            return {"type": action_type, "status": "SUCCESS", "work_order_id": work_order.id}

        if action_type == "trigger_webhook":
            payload = action.get("payload", {})
            dispatch_webhook(
                target_url=payload["target_url"],
                event_message=payload.get("event_message", {}),
            )
            return {"type": action_type, "status": "SUCCESS"}

        if action_type == "send_notification":
            payload = action.get("payload", {})
            logger.info("Agent notification", extra={"notification": payload})
            return {"type": action_type, "status": "SUCCESS", "message": payload.get("message", "")}

        return {"type": action_type, "status": "SKIPPED", "reason": "Unknown action type"}


def persist_agent_action(
    db: Session,
    agent_name: str,
    event_type: str,
    decision: str,
    actions: list[dict],
) -> AIAgentAction:
    record = AIAgentAction(
        agent_name=agent_name,
        event_type=event_type,
        decision=decision,
        actions=actions,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
