"""
Character class to represent different characters in the game
"""

from dataclasses import dataclass

@dataclass
class Character:
    title: str
    name: str

    can_see: set[str]

def get_default_characters() -> dict[Character]:
    characters: dict[Character] = {}

    characters['mayor'] = Character("mayor", "Sam Wallace", {'contracts','repairs','employees','mayor_reelection','rep_reelection','ceo_stock','substack_subs','union_rate','admiral_passage', 'mayor_funds', 'ceo_funds'})
    characters['rep'] = Character("rep", "Daryl Chase", {'contracts','repairs','employees','mayor_reelection','rep_reelection','ceo_stock','substack_subs','union_rate','admiral_passage', 'rep_funds', 'ceo_funds'})
    characters['ceo'] = Character("ceo", "Alexander Brewer", {'contracts','repairs','employees','mayor_reelection','rep_reelection','ceo_stock','substack_subs','union_rate','admiral_passage', 'ceo_funds'})
    characters['substacker'] = Character("substacker", "Ryan Carmichael", {'contracts','repairs','employees','mayor_reelection','rep_reelection','ceo_stock','substack_subs','union_rate','admiral_passage', 'ceo_funds'})
    characters['union'] = Character("union", "Tobin McKinley", {'contracts','repairs','employees','mayor_reelection','rep_reelection','ceo_stock','substack_subs','union_rate','admiral_passage', 'ceo_funds', 'union_funds'})
    characters['admiral'] = Character("admiral", "Marty Reid", {'contracts','repairs','employees','mayor_reelection','rep_reelection','ceo_stock','substack_subs','union_rate','admiral_passage', 'ceo_funds'})

    return characters