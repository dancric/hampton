"""
gamestate.py

A dataclass for storing all data related to the game from scene to scene
"""
import copy
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
class SpendingDecisions:
    mayor: SpendingDecision = SpendingDecision()
    rep: SpendingDecision = SpendingDecision()
    ceo: SpendingDecision = SpendingDecision()
    substack: SpendingDecision = SpendingDecision()
    union: SpendingDecision = SpendingDecision()
    admiral: SpendingDecision = SpendingDecision()

@dataclass
class SceneDecisions:
    scene_decision: dict = {}

    share_price: float = 0
    workforce: int = 10000

    spending_decisions: SpendingDecisions = SpendingDecisions()

def processScene1(state: GameState, decisions: SceneDecisions) -> GameState:
    new_state = copy.deepcopy(state)

    #Handle Scene Decisions
    #1-1
    new_state.contracts = decisions.scene_decision['Contracts']

    #1-2
    blame_sum = sum(decisions.scene_decision['Blame'].values()) #Players can choose 1 to all of the options and we scale accordingly
    new_state.mayor_likability -= 20 * decisions.scene_decision['Blame']['Mayor Likability'] / blame_sum
    new_state.rep_likability -= 20 * decisions.scene_decision['Blame']['Rep Likability'] / blame_sum
    new_state.union_rate += 0.2* decisions.scene_decision['Blame']['GBI'] / blame_sum
    new_state.admiral_likability = state.admiral_likability + 10 * decisions.scene_decision['Blame']['Self Blame'] / blame_sum - 20 * decisions.scene_decision['Blame']['Navy'] / blame_sum - 10 * decisions.scene_decision['Blame']['Act of God'] / blame_sum + 5 * (1-blame_sum)

    return new_state


def processSpending(state: GameState, spending_decisions: SpendingDecisions):
    """
    Processes in order all of the changes from the spending data from the 6 characters
    """

    # Mayor
    state.repairs += spending_decisions.mayor.repairs
    state.mayor_likability += spending_decisions.mayor.mayor_likability / 50000
    state.rep_likability += spending_decisions.mayor.rep_likability / 25000
    state.substack_subs *= 1.1 ^ (spending_decisions.mayor.substack_subs / 100000)
    state.union_rate += 0.01 * spending_decisions.mayor.union_rate / 50000
    state.admiral_likability += spending_decisions.mayor.admiral_likability / 250000
    
    state.mayor_funds -= spending_decisions.mayor.total()

    # Representative
    state.repairs += spending_decisions.rep.repairs
    state.mayor_likability += spending_decisions.rep.mayor_likability / 100000
    state.rep_likability += spending_decisions.rep.rep_likability / 200000
    state.substack_subs *= 1.1 ^ (spending_decisions.rep.substack_subs / 250000)
    state.union_rate += 0.01 * spending_decisions.rep.union_rate / 100000
    state.admiral_likability += spending_decisions.rep.admiral_likability / 100000
    
    state.rep_funds -= spending_decisions.rep.total()

    # CEO
    state.repairs += spending_decisions.ceo.repairs
    state.mayor_likability += spending_decisions.ceo.mayor_likability / 250000
    state.rep_likability += spending_decisions.ceo.rep_likability / 250000
    state.substack_subs *= 1.1 ^ (spending_decisions.ceo.substack_subs / 1000000)
    state.union_rate += 0.01 * spending_decisions.ceo.union_rate / 250000
    state.admiral_likability += spending_decisions.ceo.admiral_likability / 250000
    
    state.ceo_funds -= spending_decisions.ceo.total()

    # Substacker
    state.repairs += 250 * state.substack_subs * spending_decisions.substack.repairs
    state.mayor_likability += spending_decisions.substack.mayor_likability * 5
    state.rep_likability += spending_decisions.substack.rep_likability * 5
    state.substack_subs *= 1.1 ^ (spending_decisions.substack.substack_subs)
    state.union_rate += 0.05 * spending_decisions.substack.union_rate
    state.admiral_likability += spending_decisions.substack.admiral_likability * 5

    # Union President
    state.repairs += spending_decisions.union.repairs
    state.mayor_likability += spending_decisions.union.mayor_likability / 100000
    state.rep_likability += spending_decisions.union.rep_likability / 100000
    state.substack_subs *= 1.1 ^ (spending_decisions.union.substack_subs / 250000)
    state.union_rate += 0.01 * spending_decisions.union.union_rate / 100000
    state.admiral_likability += spending_decisions.union.admiral_likability / 100000
    
    state.union_funds -= spending_decisions.union.total()

    # Admiral
    state.repairs += 500000 * spending_decisions.admiral.repairs
    state.mayor_likability += spending_decisions.admiral.mayor_likability * 5
    state.rep_likability += spending_decisions.admiral.rep_likability * 5
    state.substack_subs *= 1.1 ^ (spending_decisions.admiral.substack_subs)
    state.union_rate += 0.05 * spending_decisions.admiral.union_rate
    state.admiral_likability += spending_decisions.admiral.admiral_likability * 5