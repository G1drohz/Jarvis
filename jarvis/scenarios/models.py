"""Scenario / action data models (Luxify-style)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class Action(BaseModel):
    type: str  # launch | url | key | type | wait | shell | open_path | notify | plugin
    value: str = ""
    params: dict[str, Any] = Field(default_factory=dict)


class Scenario(BaseModel):
    id: str
    name: str
    phrase: str = ""
    aliases: list[str] = Field(default_factory=list)
    actions: list[Action] = Field(default_factory=list)
    enabled: bool = True
    require_confirm: bool = False


class Collection(BaseModel):
    id: str
    name: str
    scenarios: list[Scenario] = Field(default_factory=list)
