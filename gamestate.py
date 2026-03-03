"""
gamestate.py

A dataclass for storing all data related to the game from scene to scene
"""

from dataclasses import dataclass, asdict, fields

from character import Character

@dataclass
class GameState:
    contracts: int = 0
    repairs: int = 0
    employees: int = 10000
    mayor_reelection: float = 0.2
    mayor_likability: int = 50
    rep_reelection: float = 0.2
    rep_likability: int = 50
    ceo_stock: float = 10.0
    substack_subs: int = 1000
    union_rate: float = 20.0
    admiral_passage: float = 100.0
    admiral_likability: int = 50
    mayor_funds: int = 500000
    rep_funds: int = 2500000
    ceo_funds: int = 100000000
    union_funds: int = 2000000

    def state_for(self, character: Character) -> dict:
        visible = character.can_see & {f.name for f in fields(self)} #include intersection of fields

        data = asdict(self)  # converts dataclass (recursively) to dict
        return {k: data[k] for k in visible}
    
@dataclass
class SpendingDecision:
    mayor_likability: int = 0
    rep_likability: int = 0
    union_rate: int = 0
    substack_subs: int = 0
    admiral_likability: int = 0
    repairs: int = 0

    def total(self):
        return abs(self.mayor_likability) + abs(self.rep_likability) + abs(self.union_rate) + abs(self.substack_subs) + abs(self.admiral_likability) + abs(self.repairs)

@dataclass
class Scene1Decisions:
    scene_decisions = {}
    scene_decisions['Proposed Contracts'] = 0
    scene_decisions['Blame'] = {
        "Self Blame": 0,
        "Navy": 0,
        "Congress": 0,
        "Local Government": 0,
        "GBI": 0,
        "Act of God": 0
    }

    share_price: float = 0
    workforce: int = 10000

    mayor_spending = SpendingDecision()
    rep_spending = SpendingDecision()
    ceo_spending = SpendingDecision()
    substack_spending = SpendingDecision()
    union_spending = SpendingDecision()
    admiral_spending = SpendingDecision()

def processScene1(state: GameState, decisions: Scene1Decisions):
    pass