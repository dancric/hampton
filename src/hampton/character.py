"""
Character class to represent different characters in the game
"""

from dataclasses import dataclass

characters = ["mayor", "rep", "ceo", "substacker", "union", "admiral"]

@dataclass
class Character:
    title: str
    name: str

    can_see: set[str]

    targets: list[str]

def getDefaultCharacters() -> dict[Character]:
    """
    Returns a dictionary incorproating the 6 main characters from Hampton at the Cross-Roads
    """
    characters: dict[Character] = {}

    characters['mayor'] = Character("mayor", "Sam Wallace", {'contracts','repairs','employees','mayor_reelection','rep_reelection','ceo_stock','substack_subs','union_rate','admiral_passage', 'mayor_funds', 'ceo_funds'}, ["rep", "ceo", "substacker", "union", "admiral"])
    characters['rep'] = Character("rep", "Daryl Chase", {'contracts','repairs','employees','mayor_reelection','rep_reelection','ceo_stock','substack_subs','union_rate','admiral_passage', 'rep_funds', 'ceo_funds'}, ["mayor", "ceo", "substacker", "union", "admiral"])
    characters['ceo'] = Character("ceo", "Alexander Brewer", {'contracts','repairs','employees','mayor_reelection','rep_reelection','ceo_stock','substack_subs','union_rate','admiral_passage', 'ceo_funds'}, ["mayor", "rep", "substacker", "union", "admiral"])
    characters['substacker'] = Character("substacker", "Ryan Carmichael", {'contracts','repairs','employees','mayor_reelection','rep_reelection','ceo_stock','substack_subs','union_rate','admiral_passage', 'ceo_funds'}, ["mayor", "rep", "ceo", "union", "admiral"])
    characters['union'] = Character("union", "Tobin McKinley", {'contracts','repairs','employees','mayor_reelection','rep_reelection','ceo_stock','substack_subs','union_rate','admiral_passage', 'ceo_funds', 'union_funds'}, ["mayor", "rep", "ceo", "substacker", "admiral"])
    characters['admiral'] = Character("admiral", "Marty Reid", {'contracts','repairs','employees','mayor_reelection','rep_reelection','ceo_stock','substack_subs','union_rate','admiral_passage', 'ceo_funds'}, ["mayor", "rep", "ceo", "substacker", "union"])

    return characters