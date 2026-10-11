from jarvis.core.agent import Agent


def test_agent_help():
    agent = Agent()
    reply = agent.process("help")
    assert "команд" in reply.lower() or "help" in reply.lower()


def test_agent_status():
    agent = Agent()
    reply = agent.process("status")
    assert "JARVIS" in reply or "v0.1" in reply


def test_agent_clear():
    agent = Agent()
    agent.process("привет")
    reply = agent.process("clear")
    assert "очищена" in reply.lower() or "clear" in reply.lower()
