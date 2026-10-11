"""Simple interactive console loop (optional, without UI)."""

from __future__ import annotations

from jarvis.core.agent import Agent


def console_loop(agent: Agent | None = None) -> None:
    agent = agent or Agent()
    print("JARVIS console. Type 'exit' or 'quit' to leave.")
    while True:
        try:
            user = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if user.lower() in {"exit", "quit", "q"}:
            break
        if not user:
            continue
        reply = agent.process(user)
        print(reply)
