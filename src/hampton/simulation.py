import random
from pathlib import Path
from dataclasses import dataclass, field

import dill

from .character import getDefaultCharacters
from .gamestate import GameState, SceneDecisions, SpendingDecision, SpendingDecisions, processScene1
from .agent import Agent, AgentList
from .api import API, AgentAction
from .player_decisions import get_scene_1_decisions

ROOT = Path(__file__).resolve().parents[2]
WORD_BUDGET: int = 2250


def save_actions(actions: list[AgentAction], filepath: str | Path) -> None:
    """Serialize a list of AgentAction to a file using dill."""
    data = [a.model_dump() for a in actions]
    with open(filepath, "wb") as f:
        dill.dump(data, f)


def load_actions(filepath: str | Path) -> list[AgentAction]:
    """Deserialize a list of AgentAction from a dill file."""
    with open(filepath, "rb") as f:
        data = dill.load(f)
    return [AgentAction.model_validate(d) for d in data]

@dataclass
class Simulator():
    agents: AgentList = None
    states: list = field(default_factory=list)

    def setup_simulation(self):
        """
        Setup the game state and agents for the game start
        Everything is ready before we begin Scene 1
        """

        self.states.append(GameState())
        self.agents = createStandardAgents()

        self.applySavedContext("story")
        self.applySavedContext("characters")
        self.applySavedContext("stock_price")
        self.applySavedContext("rules")
        self.applySavedContext("agent")
        self.applyCharacterContext()

    def applySavedContext(self, name: str):
        """
        Applies rulesets to every agent in the Simulator
        """

        with open(ROOT / "rules" / f"{name}.md") as f:
            context = f.read()

        for agent in self.agents:
            agent.addContext(context)

    def applyCharacterContext(self):
        """
        Convenience function for applying a character's private information to just that one agent
        """

        for agent in self.agents:
            with open(ROOT / "rules" / "characters" / f"{agent.character.title}.md") as f:
                context = f.read()
            agent.addContext(context)

    def applySceneContext(self, scene_num: int):
        """
        Applies a scene context based on the scene number
        """

        with open(ROOT / "rules" / "scenes" / f"scene_{scene_num}.md") as f:
            context = f.read()

        for agent in self.agents:
            agent.addContext(context)

    def runScene(self, scene_num: int, api: API) -> list[AgentAction]:
        budgets: dict[str, int] = {}
        actions: list[AgentAction] = []

        for agent in self.agents:
            budgets[agent.character.title] = WORD_BUDGET

        self.applySceneContext(scene_num)

        # Lookup table so we can find agents by character title
        agent_lookup: dict[str, Agent] = {
            agent.character.title: agent for agent in self.agents
        }

        # Main loop: repeat until every agent's budget is exhausted
        while max(budgets.values()) > 0:
            # The agent with the most words remaining goes next; ties broken randomly
            max_budget = max(budgets.values())
            candidates = [title for title, b in budgets.items() if b == max_budget]
            chosen_title = random.choice(candidates)
            chosen_agent = agent_lookup[chosen_title]

            # Get the agent's action from the API and tag with speaker
            raw_action = api.get_agent_action(chosen_agent, self.states[-1], budgets)
            action = AgentAction(speaker=chosen_title, **raw_action.model_dump())
            actions.append(action)

            # Add the conversation to each target's context
            context_msg = f"{chosen_title} says to {', '.join(action.targets)}: {action.message}"
            for target_title in action.targets:
                agent_lookup[target_title].addContext(context_msg)

            # Deduct word count from the speaker's budget
            word_count = len(action.message.split())
            budgets[chosen_title] -= word_count

            print(f"Action Complete - Current Word Budgets:\n{budgets}\n\n")

        return actions
    
    def run_scene_1_decisions(self, api: API) -> dict:
        """
        After the scene's conversations, each agent fills out their decision sheet.
        Returns a dict mapping character title to their parsed decision.
        """
        decision_models = get_scene_1_decisions(self.states[-1])
        decisions: dict = {}

        agent_lookup: dict[str, Agent] = {
            agent.character.title: agent for agent in self.agents
        }

        for title, model_class in decision_models.items():
            agent = agent_lookup[title]
            context = agent.agg_context()

            response = api.client.responses.parse(
                model="gpt-5.4",
                input=[
                    {
                        "role": "system",
                        "content": (
                            "You are playing a character in a policy simulation."
                            "Based on the conversations you have had, fill out your decision sheet."
                            "Think carefully about how your decisions will maximize your score."
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Character: {agent.character.title}\n"
                            f"Context:\n{context}\n\n"
                            f"Current game state:\n{self.states[-1]}\n\n"
                            "Fill out your decision sheet."
                        ),
                    },
                ],
                text_format=model_class,
            )

            decisions[title] = response.output_parsed
            print(f"Decision received from {title}")

        return decisions
    
    def process_scene_1_decisions(self, decisions):
        scene_decisions = {}
        scene_decisions['Contracts'] = decisions['admiral'].contracts
        scene_decisions['Blame'] = {}
        scene_decisions['Blame']['Self'] = decisions['admiral'].blame_self
        scene_decisions['Blame']['Navy'] = decisions['admiral'].blame_navy
        scene_decisions['Blame']['Congress'] = decisions['admiral'].blame_congress
        scene_decisions['Blame']['Local Government'] = decisions['admiral'].blame_local_government
        scene_decisions['Blame']['GBI'] = decisions['admiral'].blame_gbi
        scene_decisions['Blame']['Act of God'] = decisions['admiral'].blame_act_of_god

        scene = SceneDecisions()
        scene.scene_decisions = scene_decisions
        scene.workforce = decisions['ceo'].employment
        scene.share_price = decisions['substacker'].share_price

        # Convert each character's API spending into a SpendingDecision
        spending = SpendingDecisions()
        for title, attr in [('mayor', 'mayor'), ('rep', 'rep'), ('ceo', 'ceo'),
                            ('substacker', 'substack'), ('union', 'union'), ('admiral', 'admiral')]:
            s = decisions[title].spending if decisions.get(title) is not None else None
            if s is None:
                continue
            setattr(spending, attr, SpendingDecision(
                mayor_likability=s.mayor_positive - s.mayor_negative,
                rep_likability=s.rep_posiitve - s.rep_negative,
                union_rate=s.union_rate_positive - s.union_rate_negative,
                substack_subs=s.substack_subs_positive - s.substack_subs_negative,
                admiral_likability=s.admiral_positive - s.admiral_negative,
                repairs=s.repairs,
            ))

        scene.spending_decisions = spending
        self.states.append(processScene1(self.states[-1], scene))

def createStandardAgents() -> AgentList:
    characters = getDefaultCharacters()
    agents: AgentList = []

    for key in characters:
        agents.append(Agent(character=characters[key]))

    return agents