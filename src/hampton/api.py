from pathlib import Path

from openai import OpenAI
import tiktoken
from pydantic import BaseModel, Field
from typing import Literal
from dataclasses import dataclass
from .agent import Agent
from .gamestate import GameState

ROOT = Path(__file__).resolve().parents[2]

class AgentAction(BaseModel):
    """Module-level type for annotations. The API uses a constrained version from make_action_model."""

    speaker: str = ""
    reasoning: str = Field(description="Private reasoning in 1-3 sentences. Not shown to other characters and is used to understand your strategic thinking.")
    targets: list[str] = Field(description="The characters being spoken to. Can be just one character or a group of characters who all hear the same message")
    message: str = Field(description="What the agent says to the target list of characters. All characters hear the same message")

def make_action_model(agent: Agent):
    """
    Returns an AgentAction that constrains an agent to who it can talk to and prepares it for the API
    """

    TargetType = Literal[tuple(agent.character.targets)]

    class AgentAction(BaseModel):
        reasoning: str = Field(description="Private reasoning in 1-3 sentences. Not shown to other characters and is used to understand your strategic thinking.")
        targets: list[TargetType] = Field(description="The characters being spoken to. Can be just one character or a group of characters who all hear the same message") # type: ignore
        message: str = Field(description="What the agent says to the target list of characters. All characters hear the same message")

    return AgentAction

@dataclass
class API():
    client = None

    def connect(self):
        self.client = OpenAI(
        api_key = get_api_key()
    )

    def get_response(self, query: str):
        response = self.client.responses.create(
            model="gpt-5.2",
            input=query
        )
        return response.output_text

    def get_agent_response(self, agent: Agent, query: str):
        context = agent.agg_context()
        response = self.client.responses.create(
            model="gpt-5-mini",
            input=f"{context} \n {query}"
        )
        return response.output_text

    def get_agent_action(self, agent: Agent, state: GameState, budgets: dict[int]) -> AgentAction:
        context = agent.agg_context()
        constrained_model = make_action_model(agent)

        response = self.client.responses.parse(
            model="gpt-5-mini",
            input=[
            {
                "role": "system",
                "content": (
                    "You are playing a character in a policy simulation and want to negotiate with the other characters most effectively to maximize your score in the game"
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Character: {agent.character.title}\n"
                    f"The current game state is:\n{state}"
                    f"The remaining conversation word budgets are:\n{budgets}"
                    "Who do you want to talk to next and what do you say to them? Remember that the word count of what you say will be deducted from your word budget\n"
                ),
            },
        ],
        text_format=constrained_model
        )

        decision: AgentAction = response.output_parsed
        return decision

def count_tokens(text: str, model: str = "gpt-5-mini") -> int:
    """
    Estimates number of tokens in a query
    """
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def get_api_key() -> str:
    with open(ROOT / "key.secure") as f:
        api_key = f.read()

    return api_key