from abc import ABC, abstractmethod
from typing import TypeVar

TVozlišče = TypeVar("TVozlišče", bound="Vozlišče")
TIzraz = TypeVar("TIzraz", bound="Izraz")

class Vozlišče(ABC):
    scope: TVozlišče = None

    @abstractmethod
    def print(self, globina: int = 0):
        pass

    @abstractmethod
    def ovrednoti(self, spremenljivke: dict) -> float:
        pass

    @abstractmethod
    def compile(self) -> str:
        pass

class Izraz(Vozlišče):
    l: TIzraz
    r: TIzraz

    def __init__(self, l: TIzraz, r: TIzraz) -> None:
        self.l = l
        self.r = r

class Prazno(Vozlišče):
    def print(self, globina: int = 0) -> None:
        print(globina * "  " + "()")

    def ovrednoti(self, _: dict) -> float:
        return 0.0

    def compile(self) -> str:
        return ""

class Niz(Vozlišče):
    niz: str

    def __init__(self, niz: float) -> None:
        self.niz = niz

    def print(self, globina: int = 0) -> None:
        print(globina * "  " + f'"{self.niz}"')

    def ovrednoti(self, _: dict) -> float:
        return self.niz

    def compile(self) -> str:
        return f'PUSH "{self.niz}"\n'

class Število(Vozlišče):
    število: float

    def __init__(self, število: float) -> None:
        self.število = število

    def print(self, globina: int = 0) -> None:
        print(globina * "  " + str(self.število))

    def ovrednoti(self, _: dict) -> float:
        return self.število

    def compile(self) -> str:
        return f"PUSH #{self.število}\n"

class Spremenljivka(Vozlišče):
    ime: str
    poz_na_kopici: int

    def __init__(self, ime: float, pozicija: int = None) -> None:
        self.ime = ime
        self.poz_na_kopici = pozicija

    def print(self, globina: int = 0):
        print(globina * "  " + f"{self.ime} @{self.poz_na_kopici}")

    def ovrednoti(self, spremenljivke = dict()) -> float:
        return 0.0

    def compile(self) -> str:
        return f"PUSH @{self.poz_na_kopici}\n"

class Potenca(Izraz):
    def print(self, globina: int = 0):
        print(globina * "  " + '^')
        self.l.print(globina + 1)
        self.r.print(globina + 1)

    def ovrednoti(self, spremenljivke = dict()) -> float:
        return self.l.ovrednoti(spremenljivke) ** self.r.ovrednoti(spremenljivke)

    def compile(self) -> str:
        return (
            f"{self.l.compile()}"
            f"{self.r.compile()}"
             "POW\n"
        )

class Množenje(Izraz):
    def print(self, globina: int = 0):
        print(globina * "  " + '*')
        self.l.print(globina + 1)
        self.r.print(globina + 1)

    def ovrednoti(self, spremenljivke = dict()) -> float:
        return self.l.ovrednoti(spremenljivke) * self.r.ovrednoti(spremenljivke)

    def compile(self) -> str:
        return (
            f"{self.l.compile()}"
            f"{self.r.compile()}"
             "MUL\n"
        )

class Deljenje(Izraz):
    def print(self, globina: int = 0):
        print(globina * "  " + '/')
        self.l.print(globina + 1)
        self.r.print(globina + 1)

    def ovrednoti(self, spremenljivke = dict()) -> float:
        return self.l.ovrednoti(spremenljivke) / self.r.ovrednoti(spremenljivke)

    def compile(self) -> str:
        return (
            f"{self.l.compile()}"
            f"{self.r.compile()}"
             "DIV\n"
        )

class Seštevanje(Izraz):
    def print(self, globina: int = 0):
        print(globina * "  " + '+')
        self.l.print(globina + 1)
        self.r.print(globina + 1)

    def ovrednoti(self, spremenljivke = dict()) -> float:
        return self.l.ovrednoti(spremenljivke) + self.r.ovrednoti(spremenljivke)

    def compile(self) -> str:
        return (
            f"{self.l.compile()}"
            f"{self.r.compile()}"
             "ADD\n"
        )

class Odštevanje(Izraz):
    def print(self, globina: int = 0):
        print(globina * "  " + '+')
        self.l.print(globina + 1)
        self.r.print(globina + 1)

    def ovrednoti(self, spremenljivke = dict()) -> float:
        return self.l.ovrednoti(spremenljivke) - self.r.ovrednoti(spremenljivke)

    def compile(self,) -> str:
        return (
            f"{self.l.compile()}"
            f"{self.r.compile()}"
             "SUB\n"
        )

class Priredba(Vozlišče):
    spremenljivka: Spremenljivka
    izraz: Izraz
    nova_spr: bool

    def __init__(self, spremenljivka: Spremenljivka, izraz: Izraz, nova_spr: bool) -> None:
        self.spremenljivka = spremenljivka
        self.izraz = izraz
        self.nova_spr = nova_spr

    def print(self, globina: int = 0):
        print(globina * "  " + f"{self.spremenljivka.ime} =")
        self.izraz.print(globina + 1)

    def ovrednoti(self, spremenljivke = dict()) -> float:
        spremenljivke[self.spremenljivka.ime] = self.izraz.ovrednoti(spremenljivke)
        return spremenljivke[self.spremenljivka.ime]

    def compile(self) -> str:
        stavki = self.izraz.compile()

        if not self.nova_spr:
            stavki += (
                f"MOV @{self.spremenljivka.poz_na_kopici}\n"
                 "POP\n"
            )
        return stavki

TZaporedje = TypeVar("TZaporedje", bound="Zaporedje")

class Zaporedje(Izraz):
    def __init__(self, zaporedje: Izraz, priredba: Priredba) -> None:
        self.l = zaporedje
        self.r = priredba

    def print(self, globina: int = 0):
        self.l.print(globina)
        print(globina * "  " + ";")
        self.r.print(globina + 1)

    def ovrednoti(self, spremenljivke: dict) -> float:
        self.l.ovrednoti(spremenljivke)
        return self.r.ovrednoti(spremenljivke)

    def compile(self) -> str:
        return (
            f"{self.l.compile()}"
            f"{self.r.compile()}"
        )

class Scope(Vozlišče):
    zaporedje: Zaporedje

    def __init__(self, zaporedje: Zaporedje) -> None:
        self.zaporedje = zaporedje

    def print(self, globina: int = 0):
        print(globina * "  " + "{")
        self.zaporedje.print(globina+1)
        print(globina * "  " + "}")

    def ovrednoti(self, spremenljivke: dict) -> float:
        return self.zaporedje.ovrednoti(spremenljivke)

    def compile(self, st_spr: int) -> str:
        return (
            f"{self.zaporedje.compile()}"
            "POP\n" * st_spr
        )

class FunkcijskiKlic(Vozlišče):
    ime: str
    argumenti: list[Izraz]
    ukazi: Scope

    def __init__(self, ime: str, ukaz: str, argumenti: list[Izraz], ukazi: Vozlišče) -> None:
        self.ime = ime
        self.ukaz = ukaz
        self.argumenti = argumenti
        self.ukazi = ukazi

    def print(self, globina: int = 0):
        print(globina * "  " + "{")
        self.zaporedje.print(globina+1)
        print(globina * "  " + "}")

    def ovrednoti(self, spremenljivke: dict) -> float:
        return self.argumenti[0].ovrednoti(spremenljivke)

    def compile(self) -> str:
        ukazi = ""
        for argument in self.argumenti:
            ukazi += argument.compile()
        ukazi += self.ukaz + '\n'
        ukazi += "POP\n" * len(self.argumenti)

        return ukazi

class Print(Vozlišče):
    izrazi: list[Izraz]

    def __init__(self, izrazi: list[Izraz]) -> None:
        self.izrazi = izrazi

    def print(self, globina: int = 0):
        print(globina * "  " + "print(")
        for izraz in self.izrazi[:-1]:
            izraz.print(globina + 1)
            print(",")
        self.izrazi[-1].print(globina + 1)
        print(globina * "  " + ")")

    def ovrednoti(self, spremenljivke = dict()) -> float:
        return None

    def compile(self) -> str:
        ukazi = ""
        for izraz in self.izrazi:
            ukazi += izraz.compile()
            ukazi += "PRINT\n"
            ukazi += "POP\n"
        return ukazi
