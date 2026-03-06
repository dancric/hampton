from pathlib import Path
from dataclasses import dataclass

from character import getDefaultCharacters
from gamestate import GameState
from agent import Agent, AgentList
from api import getResponse

ROOT = Path(__file__).resolve().parents[2]

@dataclass
class Simulator():
    states: list = list()
    agents: AgentList

    def setup_simulation(self):
        self.states.append(GameState())

        self.agents = createStandardAgents()
        self.applySavedContext("story")
        self.applySavedContext("characters")
        self.applySavedContext("stock_price")
        self.applySavedContext("rules")
        self.applySavedContext("agent")
        self.applyCharacterContext()

        #Start First Scene
        self.applySceneContext(1)

    def applySavedContext(self, name: str):
        with open(ROOT / "rules" / f"{name}.md") as f:
            context = f.read()

        for agent in self.agents:
            agent.addContext(context)

    def applyCharacterContext(self):
        for agent in self.agents:
            with open(ROOT / "rules" / "characters" / f"{agent.character.title}.md") as f:
                context = f.read()
            agent.addContext(context)

    def applySceneContext(self, scene_num: int):
        with open(ROOT / "rules" / "scenes" / f"scene_{scene_num}.md") as f:
            context = f.read()

        for agent in self.agents:
            agent.addContext(context)

def createStandardAgents() -> AgentList:
    characters = getDefaultCharacters()
    agents: AgentList = list(Agent)

    for key in characters:
        agents.append(Agent(character=characters[key]))

    return agents