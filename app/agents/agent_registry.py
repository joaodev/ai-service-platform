from __future__ import annotations

import os

from sqlalchemy.orm import Session

from app.agents.agent_engine import AgentActionExecutor, AgentEvent, BaseAgent
from app.events.event_types import EventType


class TicketAgent(BaseAgent):
    name = "TicketAgent"
    events_subscribed = [EventType.TICKET_CREATED, EventType.TICKET_UPDATED]

    def evaluate(self, event: AgentEvent) -> dict:
        priority = event.payload.get("priority")
        if priority == "HIGH":
            return {
                "decision": "High priority ticket detected; notify operations",
                "actions": [
                    {
                        "type": "send_notification",
                        "payload": {
                            "message": f"High priority ticket #{event.payload.get('id')} created",
                            "ticket_id": event.payload.get("id"),
                        },
                    }
                ],
            }
        return {"decision": "No action required", "actions": []}

    def execute(self, db: Session, actions: list[dict]) -> list[dict]:
        return [AgentActionExecutor.execute_action(db, action) for action in actions]


class FinanceAgent(BaseAgent):
    name = "FinanceAgent"
    events_subscribed = [EventType.PAYMENT_RECEIVED, EventType.TRANSACTION_CREATED]

    def evaluate(self, event: AgentEvent) -> dict:
        amount = float(event.payload.get("amount", 0))
        actions = []
        decision = "No action required"

        if event.event_type == EventType.PAYMENT_RECEIVED and amount >= 10000:
            decision = "High value payment; notify finance audit"
            actions.append(
                {
                    "type": "send_notification",
                    "payload": {
                        "message": f"High value payment detected: {amount}",
                        "transaction_id": event.payload.get("id"),
                    },
                }
            )

        return {"decision": decision, "actions": actions}

    def execute(self, db: Session, actions: list[dict]) -> list[dict]:
        return [AgentActionExecutor.execute_action(db, action) for action in actions]


class OperationsAgent(BaseAgent):
    name = "OperationsAgent"
    events_subscribed = [EventType.WORK_ORDER_STARTED, EventType.WORK_ORDER_FINISHED]

    def evaluate(self, event: AgentEvent) -> dict:
        if event.event_type == EventType.WORK_ORDER_FINISHED:
            return {
                "decision": "Work order finished; notify completion",
                "actions": [
                    {
                        "type": "send_notification",
                        "payload": {
                            "message": f"Work order #{event.payload.get('id')} finished",
                            "work_order_id": event.payload.get("id"),
                        },
                    }
                ],
            }
        return {"decision": "No action required", "actions": []}

    def execute(self, db: Session, actions: list[dict]) -> list[dict]:
        return [AgentActionExecutor.execute_action(db, action) for action in actions]


class AutomationAgent(BaseAgent):
    name = "AutomationAgent"
    events_subscribed = [
        EventType.SERVICE_CREATED,
        EventType.KNOWLEDGE_ARTICLE_CREATED,
    ]

    def evaluate(self, event: AgentEvent) -> dict:
        webhook_url = os.getenv("AGENT_AUTOMATION_WEBHOOK_URL", "")
        if not webhook_url:
            return {"decision": "No automation webhook configured", "actions": []}

        return {
            "decision": "Forward event to automation webhook",
            "actions": [
                {
                    "type": "trigger_webhook",
                    "payload": {
                        "target_url": webhook_url,
                        "event_message": {
                            "event_type": event.event_type,
                            "payload": event.payload,
                            "context": event.context,
                        },
                    },
                }
            ],
        }

    def execute(self, db: Session, actions: list[dict]) -> list[dict]:
        return [AgentActionExecutor.execute_action(db, action) for action in actions]


def get_registered_agents() -> list[BaseAgent]:
    return [
        TicketAgent(),
        FinanceAgent(),
        OperationsAgent(),
        AutomationAgent(),
    ]
