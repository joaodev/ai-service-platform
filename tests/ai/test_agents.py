import pytest


@pytest.mark.ai
def test_run_agent_falls_back_without_external_ai(test_db_session, admin_user, monkeypatch):
    from app.ai import agent as agent_module
    from app.models.ai_agent_log import AIAgentLog

    monkeypatch.setattr(agent_module, "AZURE_OPENAI_ENDPOINT", "")
    monkeypatch.setattr(agent_module, "AZURE_OPENAI_API_KEY", "")
    monkeypatch.setattr(agent_module, "AZURE_OPENAI_CHAT_DEPLOYMENT", "")

    result = agent_module.run_agent(
        db=test_db_session,
        user=admin_user,
        message="Create an operational summary.",
    )

    assert "not configured" in result["agent_response"]
    log = test_db_session.query(AIAgentLog).one()
    assert log.user_id == admin_user.id
    assert log.actions_taken == []


@pytest.mark.ai
def test_event_agent_runner_persists_actions_with_mocked_rag(test_db_session, monkeypatch):
    from app.agents import agent_runner
    from app.models.ai_agent_action import AIAgentAction

    monkeypatch.setattr(
        agent_runner,
        "answer_question",
        lambda question: {
            "answer": "mocked operational context",
            "sources": [{"id": 1, "content": "runbook", "metadata": {"source": "test"}}],
        },
    )

    result = agent_runner.run_agents_for_event(
        db=test_db_session,
        event_type="TICKET_CREATED",
        payload={"id": 10, "priority": "HIGH", "approved": False},
    )

    assert result["agents_evaluated"] == 1
    assert result["context"]["rag_answer"] == "mocked operational context"

    action = (
        test_db_session.query(AIAgentAction).filter(AIAgentAction.agent_name == "TicketAgent").one()
    )
    execution_results = action.actions["execution_results"]
    assert execution_results[0]["type"] == "send_notification"
    assert execution_results[0]["status"] == "SUCCESS"
