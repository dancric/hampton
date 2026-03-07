from pydantic import BaseModel, Field, model_validator
from hampton.gamestate import GameState

def make_spending_model(budget: int):
    class SpendingDecisionModel(BaseModel):
        mayor_positive: int = Field(ge=0, description="Spend on positive PR for the mayor")
        mayor_negative: int = Field(ge=0, description="Spend on negative PR for the mayor")
        rep_posiitve: int = Field(ge=0, description="Spend on positive PR for the rep")
        rep_negative: int = Field(ge=0, description="Spend on negative PR for the rep")
        union_rate_positive: int = Field(ge=0, description="Spend on positive PR for the union")
        union_rate_negative: int = Field(ge=0, description="Spend on negative PR for the union")
        substack_subs_positive: int = Field(ge=0, description="Spend on positive PR for the substacker")
        substack_subs_negative: int = Field(ge=0, description="Spend on negative PR for the substacker")
        admiral_positive: int = Field(ge=0, description="Spend on positive PR for the admiral")
        admiral_negative: int = Field(ge=0, description="Spend on negative PR for the admiral")
        repairs: int = Field(ge=0, description="Spend on shipyard repairs")

        @model_validator(mode="after")
        def check_budget(self):
            spending_fields = [
                "mayor_positive", "mayor_negative", "rep_posiitve", "rep_negative",
                "union_rate_positive", "union_rate_negative", "substack_subs_positive",
                "substack_subs_negative", "admiral_positive", "admiral_negative", "repairs",
            ]
            total = sum(getattr(self, f) for f in spending_fields)

            if total > self.budget:
                scale = self.budget / total
                for f in spending_fields:
                    setattr(self, f, int(getattr(self, f) * scale))

            return self

def get_scene_1_decisions(state: GameState):
    decisions = {}

    #mayor
    MayorSpending = make_spending_model(state.mayor_funds)
    class MayorModel(BaseModel):
        spending: MayorSpending  # type: ignore[valid-type]
        reasoning: str = Field(description="Private reasoning in 1-3 paragraphs. Not shown to other characters and is used to understand your strategic thinking.")

    decisions['mayor'] = MayorModel

    #rep
    RepSpending = make_spending_model(state.rep_funds)
    class RepModel(BaseModel):
        spending: RepSpending  # type: ignore[valid-type]
        reasoning: str = Field(description="Private reasoning in 1-3 paragraphs. Not shown to other characters and is used to understand your strategic thinking.")

    decisions['rep'] = RepModel

    #ceo
    CEOSpending = make_spending_model(state.ceo_funds)
    class CEOModel(BaseModel):
        employment: int = Field(ge=0, description="Select an employment level for GBI")
        spending: CEOSpending  # type: ignore[valid-type]
        reasoning: str = Field(description="Private reasoning in 1-3 paragraphs. Not shown to other characters and is used to understand your strategic thinking.")

    decisions['ceo'] = CEOModel

    #substacker
    SubstackerSpending = make_spending_model(3)
    class SubstackerModel(BaseModel):
        share_price: float = Field(ge=0, description="Predict the share price of GBI after this scene and the decisions are made by all players")
        spending: SubstackerSpending  # type: ignore[valid-type]
        reasoning: str = Field(description="Private reasoning in 1-3 paragraphs. Not shown to other characters and is used to understand your strategic thinking.")

    decisions['substacker'] = SubstackerModel

    #union
    UnionSpending = make_spending_model(state.union_funds)
    class UnionModel(BaseModel):
        spending: UnionSpending  # type: ignore[valid-type]
        reasoning: str = Field(description="Private reasoning in 1-3 paragraphs. Not shown to other characters and is used to understand your strategic thinking.")

    decisions['union'] = UnionModel

    #admiral
    AdmiralSpending = make_spending_model(3)
    class AdmiralModel(BaseModel):
        contracts: int = Field(ge=0, le=3, description="Set the number of carrier contracts offered by the U.S. Navy. Can be 0, 1, 2 or 3.")
        blame_self: int = Field(ge=0, le=1, description="Blame yourself for what happened with the navy's shipyard")
        blame_navy: int = Field(ge=0, le=1, description="Blame the Navy as an institution for what happened with the shipyard")
        blame_congress: int = Field(ge=0, le=1, description="Blame Congress for what happened with the navy's shipyard")
        blame_local_government: int = Field(ge=0, le=1, description="Blame the local government for what happened with the navy's shipyard")
        blame_gbi: int = Field(ge=0, le=1, description="Blame GBI as the owner of the shipyard for what happened with the navy's shipyard")
        blame_act_of_god: int = Field(ge=0, le=1, description="Blame an act of god for what happened with the navy's shipyard")
        spending: AdmiralSpending  # type: ignore[valid-type]
        reasoning: str = Field(description="Private reasoning in 1-3 paragraphs. Not shown to other characters and is used to understand your strategic thinking.")

    decisions['admiral'] = AdmiralModel

    return decisions