"""Srpski traži drugačiji oblik imenice uz 1, uz 2-4 i uz 5 i više,
pri čemu brojevi 11-14 idu uz oblik za 5 i više."""


def oblik(broj, jednina, paukal, mnozina):
    poslednje_dve = broj % 100
    poslednja = broj % 10

    if poslednje_dve < 11 or poslednje_dve > 14:
        if poslednja == 1:
            return f"{broj} {jednina}"
        if 2 <= poslednja <= 4:
            return f"{broj} {paukal}"

    return f"{broj} {mnozina}"


def stavki(broj):
    """Za rečenicu oblika „zajedno sa ...“."""
    return oblik(broj, "stavkom", "stavke", "stavki")
