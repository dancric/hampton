from pathlib import Path

from openai import OpenAI
import tiktoken
from pydantic import BaseModel, Field
from typing import Literal
from agent import Agent

from character import characters

ROOT = Path(__file__).resolve().parents[2]

def makeCharacterChoiceModel(agent: Agent):
    TargetType = Literal[tuple(agent.character.target)]
    

class CharacterChoice(BaseModel):
    character: Literal["mayor","rep", "ceo", "substacker", "union", "admiral"]

    thoughts: str = Field(
        description="Private reasoning in 1-3 sentences. Not shown to other characters."
    )


def get_api_key() -> str:
    with open(ROOT / "key.secure") as f:
        api_key = f.read()

    return api_key

client = OpenAI(
    api_key = get_api_key()
)

def getResponse(query: str):
    response = client.responses.create(
        model="gpt-5.2",
        input=query
    )
    return response.output_text

def getAgentResponse(agent: Agent, query: str):
    context = agent.agg_context()
    response = client.responses.create(
        model="gpt-5-mini",
        input=f"{context} \n {query}"
    )
    return response.output_text

def getAgentNextTarget(agent: Agent) -> CharacterChoice:
    context = agent.agg_context()

    response = client.responses.parse(
        model="gpt-5-mini",
        input=[
        {
            "role": "system",
            "content": (
                "You are simulating the private thoughts of the character. "
                "Choose exactly one target from the allowed list, and explain briefly."
            ),
        },
        {
            "role": "user",
            "content": (
                "Character: Mayor\n"
                "Who do you want to talk to next?\n"
                "Allowed targets: rep, ceo, substacker, union, admiral"
            ),
        },
    ],
    text_format=CharacterChoice
    )

    decision: CharacterChoice = response.output_parsed
    return decision

def count_tokens(text: str, model: str = "gpt-5-mini") -> int:
    """
    Estimates number of tokens in a query
    """
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))