from dataclasses import dataclass, fields, field
from typing import TypeAlias
from .character import Character

StringList: TypeAlias = list[str]

@dataclass
class Agent:
    character: Character
    context: StringList = field(default_factory=list)

    def addContext(self, text:str):
        self.context.append(text)

    def agg_context(self) -> str:
        return "".join(self.context)

AgentList: TypeAlias = list[Agent]