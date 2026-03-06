"""
gamestate.py

A dataclass for storing all data related to the game from scene to scene
"""
import copy
from dataclasses import dataclass, asdict, fields, field

from .character import Character

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
    union_rate: float = 0.2
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
        return sum(abs(getattr(self,f.name)) for f in fields(self)) #must do abs since the decisions can be positive or negative spend

@dataclass
class SpendingDecisions:
    mayor: SpendingDecision = field(default_factory=SpendingDecision)
    rep: SpendingDecision = field(default_factory=SpendingDecision)
    ceo: SpendingDecision = field(default_factory=SpendingDecision)
    substack: SpendingDecision = field(default_factory=SpendingDecision)
    union: SpendingDecision = field(default_factory=SpendingDecision)
    admiral: SpendingDecision = field(default_factory=SpendingDecision)

@dataclass
class SceneDecisions:
    scene_decisions: dict = field(default_factory=dict)

    share_price: float = 0
    workforce: int = 10000

    spending_decisions: SpendingDecisions = field(default_factory=SpendingDecisions)

def burn(state: GameState):
    """
    Function to handle "burn" down of key metrics that repeat every scene
    """

    state.mayor_likability -= 10
    state.rep_likability -= 10
    state.substack_subs *= 0.95
    state.admiral_likability -= 10

def processScene1(current_state: GameState, decisions: SceneDecisions) -> GameState:
    next_state = copy.deepcopy(current_state)

    #Handle Spending Decisions
    #We do this so that Substack subscribers are properly calculated here
    processSpending(next_state, decisions.spending_decisions)

    #Burn
    burn(next_state)

    #Event Handling
    #TKTK TODO

    #Handle Scene Decisions
    #1-1
    next_state.contracts = decisions.scene_decisions['Contracts']

    #1-2
    blame_sum = sum(decisions.scene_decisions['Blame'].values()) #Players can choose 1 to all of the options and we scale accordingly
    next_state.mayor_likability -= 20 * decisions.scene_decisions['Blame']['Local Government'] / blame_sum
    next_state.rep_likability -= 20 * decisions.scene_decisions['Blame']['Congress'] / blame_sum
    next_state.union_rate += 0.2* decisions.scene_decisions['Blame']['GBI'] / blame_sum
    next_state.admiral_likability =  next_state.admiral_likability + 10 * decisions.scene_decisions['Blame']['Self Blame'] / blame_sum - 20 * decisions.scene_decisions['Blame']['Navy'] / blame_sum - 10 * decisions.scene_decisions['Blame']['Act of God'] / blame_sum + 5 * (1-blame_sum)

    #Handle Recurring Decisions

    #Workforce
    next_state.employees = decisions.workforce

    #If there are layoffs, the union rate goes down as employees fear for their jobs in an open shop workplace
    if decisions.workforce < current_state.employees:
        next_state.union_rate -= current_state.union_rate * 0.5
    else:
        next_state.union_rate += current_state.union_rate * decisions.workforce / current_state.employees - current_state.union_rate

    #Finalize next state
    capMetrics(next_state)
    recalculateMetrics(next_state, decisions.share_price)
    replenishFunds(next_state)

    return next_state


def processSpending(state: GameState, spending_decisions: SpendingDecisions):
    """
    Processes in order all of the changes from the spending data from the 6 characters
    """

    # Mayor
    state.repairs += spending_decisions.mayor.repairs
    state.mayor_likability += spending_decisions.mayor.mayor_likability / 50000
    state.rep_likability += spending_decisions.mayor.rep_likability / 25000
    state.substack_subs *= 1.1 ** (spending_decisions.mayor.substack_subs / 100000)
    state.union_rate += 0.01 * spending_decisions.mayor.union_rate / 50000
    state.admiral_likability += spending_decisions.mayor.admiral_likability / 250000
    
    state.mayor_funds -= spending_decisions.mayor.total()

    # Representative
    state.repairs += spending_decisions.rep.repairs
    state.mayor_likability += spending_decisions.rep.mayor_likability / 100000
    state.rep_likability += spending_decisions.rep.rep_likability / 200000
    state.substack_subs *= 1.1 ** (spending_decisions.rep.substack_subs / 250000)
    state.union_rate += 0.01 * spending_decisions.rep.union_rate / 100000
    state.admiral_likability += spending_decisions.rep.admiral_likability / 100000
    
    state.rep_funds -= spending_decisions.rep.total()

    # CEO
    state.repairs += spending_decisions.ceo.repairs
    state.mayor_likability += spending_decisions.ceo.mayor_likability / 250000
    state.rep_likability += spending_decisions.ceo.rep_likability / 250000
    state.substack_subs *= 1.1 ** (spending_decisions.ceo.substack_subs / 1000000)
    state.union_rate += 0.01 * spending_decisions.ceo.union_rate / 250000
    state.admiral_likability += spending_decisions.ceo.admiral_likability / 250000
    
    state.ceo_funds -= spending_decisions.ceo.total()

    # Substacker
    state.repairs += 250 * state.substack_subs * spending_decisions.substack.repairs
    state.mayor_likability += spending_decisions.substack.mayor_likability * 5
    state.rep_likability += spending_decisions.substack.rep_likability * 5
    state.substack_subs *= 1.1 ** (spending_decisions.substack.substack_subs)
    state.union_rate += 0.05 * spending_decisions.substack.union_rate
    state.admiral_likability += spending_decisions.substack.admiral_likability * 5

    # Union President
    state.repairs += spending_decisions.union.repairs
    state.mayor_likability += spending_decisions.union.mayor_likability / 100000
    state.rep_likability += spending_decisions.union.rep_likability / 100000
    state.substack_subs *= 1.1 ** (spending_decisions.union.substack_subs / 250000)
    state.union_rate += 0.01 * spending_decisions.union.union_rate / 100000
    state.admiral_likability += spending_decisions.union.admiral_likability / 100000
    
    state.union_funds -= spending_decisions.union.total()

    # Admiral
    state.repairs += 500000 * spending_decisions.admiral.repairs
    state.mayor_likability += spending_decisions.admiral.mayor_likability * 5
    state.rep_likability += spending_decisions.admiral.rep_likability * 5
    state.substack_subs *= 1.1 ** (spending_decisions.admiral.substack_subs)
    state.union_rate += 0.05 * spending_decisions.admiral.union_rate
    state.admiral_likability += spending_decisions.admiral.admiral_likability * 5

def capMetrics(state: GameState):
    """
    Check if any of the metrics are outside of bounds (and if they are, bring them back to their min or max as appropriate)
    """

    #Mayoral Likability (Mayor)
    if state.mayor_likability < 0:
        state.mayor_likability = 0
    elif state.mayor_likability > 100:
        state.mayor_likability = 100

    #Representative Likability (Representative)
    if state.rep_likability < 0:
        state.rep_likability = 0
    elif state.rep_likability > 100:
        state.rep_likability = 100

    #Union Membership Rate (Union Pres)
    if state.union_rate < 0:
        state.union_rate = 0
    elif state.union_rate > 100:
        state.union_rate = 1

    #Admiral Likability (Admiral)
    if state.admiral_likability < 0:
        state.admiral_likability = 0
    elif state.admiral_likability > 100:
        state.admiral_likability = 100

def recalculateMetrics(state: GameState, share_price: float):
    #Probability of Reelection (Mayor)
    state.mayor_reelection = 0.25 * state.employees / 45000 + 0.25 * state.union_rate + 0.5 * state.mayor_likability / 100

    #Probability of Reelection (Representative)
    state.rep_reelection = 0.25 * state.employees / 45000 + 0.25 * (1-state.union_rate) + 0.5 * state.rep_likability / 100

    #Probability of Passage (Admiral)
    state.admiral_passage = 0.15 * (4-state.contracts) + 0.2 * state.repairs / 100000000 + 0.2 * state.admiral_likability / 100

    if state.contracts == 0:
        state.admiral_passage += 0.2 #With no contracts, we can't divide by zero, so just give full credit
    else:
        state.admiral_passage += 0.2 * state.employees / (state.contracts * 10000)

    #Stock Price
    labor_cost = 100000 * state.employees + 200000 * state.employees * state.union_rate
    margin = state.contracts * 5000000000 
    state.ceo_stock = 5 * state.admiral_passage * (margin - labor_cost) / 1000000000 + 10 * state.ceo_funds / 100000000

    #Substack subscribers
    difference = abs(state.ceo_stock - share_price)
    if difference < 2.6:
        state.substack_subs *= 12
    else:
        state.substack_subs *= 5/((difference-2.5) ** 0.4) - 0.5
    
def replenishFunds(state: GameState):
    state.mayor_funds += 500000
    state.rep_funds += 2500000
    state.union_funds += 200 * state.employees * state.union_rate