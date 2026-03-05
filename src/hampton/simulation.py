from pathlib import Path

from character import getDefaultCharacters
from gamestate import GameState
from agent import Agent, AgentList
from api import getResponse

ROOT = Path(__file__).resolve().parents[2]

def run_simulation():
    states = []
    states.add[GameState()]

    agents: AgentList = createStandardAgents()
    applySavedContext(agents, "story")
    applySavedContext(agents, "characters")
    applySavedContext(agents, "stock_price")
    applySavedContext(agents, "rules")
    applySavedContext(agents, "agent")
    applyCharacterContext(agents)

    #Start First Scene
    applySceneContext(agents, 1)

    simulateScene(agents)

def createStandardAgents() -> list:
    characters = getDefaultCharacters()
    agents = []

    for char in characters:
        agents.add(Agent(character=char))

def applySavedContext(agents: AgentList, name: str):
    with open(ROOT / "rules" / f"{name}.md") as f:
        context = f.read()

    for agent in agents:
        agent.addContext(context)

def applyCharacterContext(agents: AgentList):
    for agent in agents:
        with open(ROOT / "rules" / "characters" / f"{agent.character.name}.md") as f:
            context = f.read()
        agent.addContext(context)

def applySceneContext(agents: AgentList, scene_num: int):
    with open(ROOT / "rules" / "scenes" / f"scene_{scene_num}.md") as f:
        context = f.read()

    for agent in agents:
        agent.addContext(context)

def simulateScene(agents: AgentList):
    pass