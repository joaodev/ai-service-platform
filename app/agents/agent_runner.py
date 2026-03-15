from __future__ import annotations

from sqlalchemy.orm import Session

from app.agents.agent_engine import AgentActionExecutor, AgentEvent, persist_agent_action
from app.agents.agent_registry import get_registered_agents
from app.ai.rag_service import answer_question


def _build_context(event_type: str, payload: dict) -> dict:
    question = (
        f"Given event {event_type}, what operational context should agents use? Payload: {payload}"
    )
    rag_result = answer_question(question)
    return {
        "rag_answer": rag_result.get("answer", ""),
        "rag_sources": rag_result.get("sources", []),
    }


def run_agents_for_event(db: Session, event_type: str, payload: dict) -> dict:
    context = _build_context(event_type=event_type, payload=payload)
    event = AgentEvent(event_type=event_type, payload=payload, context=context)

    executed_agents: list[dict] = []

    for agent in get_registered_agents():
        if event_type not in agent.events_subscribed:
            continue

        evaluation = agent.evaluate(event)
        decision = evaluation.get("decision", "No decision")
        proposed_actions = evaluation.get("actions", [])

        safe_actions, warnings = AgentActionExecutor.enforce_safety(payload, proposed_actions)
        execution_results = agent.execute(db=db, actions=safe_actions) if safe_actions else []

        persist_agent_action(
            db=db,
            agent_name=agent.name,
            event_type=event_type,
            decision=decision,
            actions={
                "proposed": proposed_actions,
                "approved_for_execution": safe_actions,
                "warnings": warnings,
                "execution_results": execution_results,
            },
        )

        executed_agents.append(
            {
                "agent_name": agent.name,
                "decision": decision,
                "warnings": warnings,
                "execution_results": execution_results,
            }
        )

    return {
        "event_type": event_type,
        "context": context,
        "agents_evaluated": len(executed_agents),
        "agents": executed_agents,
    }
