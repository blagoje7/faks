"""Oblik imenice uz broj: 1 stavka, 3 stavke, 5 stavki."""


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
    return oblik(broj, "stavkom", "stavke", "stavki")
