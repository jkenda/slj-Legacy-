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
    def compile(self) -> str:
        pass

class Izraz(Vozlišče):
    l: TIzraz
    r: TIzraz

    def __init__(self, l: TIzraz, r: TIzraz):
        self.l = l
        self.r = r

class Prazno(Vozlišče):
    def print(self, globina: int = 0):
        print(globina * "  " + "()")

    def compile(self) -> str:
        return ""

class Niz(Vozlišče):
    niz: str

    def __init__(self, niz: float):
        self.niz = niz

    def print(self, globina: int = 0):
        print(globina * "  " + f'"{self.niz}"')

    def compile(self) -> str:
        return f'PUSH "{self.niz}"\n'

class Število(Vozlišče):
    število: float

    def __init__(self, število: float):
        self.število = število

    def print(self, globina: int = 0):
        print(globina * "  " + str(self.število))

    def compile(self) -> str:
        return f"PUSH #{self.število}\n"

class Spremenljivka(Vozlišče):
    ime: str
    poz_na_kopici: int

    def __init__(self, ime: str, pozicija: int = None):
        self.ime = ime
        self.poz_na_kopici = pozicija

    def print(self, globina: int = 0):
        print(globina * "  " + f"({self.ime} @{self.poz_na_kopici})")

    def compile(self) -> str:
        return f"PUSH @{self.poz_na_kopici}\n"

class Potenca(Izraz):
    def print(self, globina: int = 0):
        print(globina * "  " + '^')
        self.l.print(globina + 1)
        self.r.print(globina + 1)

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

    def compile(self) -> str:
        return (
            f"{self.l.compile()}"
            f"{self.r.compile()}"
             "DIV\n"
        )

class Modulo(Izraz):
    def print(self, globina: int = 0):
        print(globina * "  " + '%')
        self.l.print(globina + 1)
        self.r.print(globina + 1)

    def compile(self) -> str:
        return (
            f"{self.l.compile()}"
            f"{self.r.compile()}"
             "MOD\n"
        )

class Seštevanje(Izraz):
    def print(self, globina: int = 0):
        print(globina * "  " + '+')
        self.l.print(globina + 1)
        self.r.print(globina + 1)

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

    def __init__(self, spremenljivka: Spremenljivka, izraz: Izraz, nova_spr: bool):
        self.spremenljivka = spremenljivka
        self.izraz = izraz
        self.nova_spr = nova_spr

    def print(self, globina: int = 0):
        print(globina * "  " + f"({self.spremenljivka.ime} @{self.spremenljivka.poz_na_kopici}) =")
        self.izraz.print(globina + 1)

    def compile(self) -> str:
        stavki = self.izraz.compile()

        if not self.nova_spr:
            stavki += (
                f"MOV @{self.spremenljivka.poz_na_kopici}\n"
                 "POP\n"
            )
        return stavki

class Zaporedje(Izraz):
    def __init__(self, zaporedje: Izraz, priredba: Priredba):
        self.l = zaporedje
        self.r = priredba

    def print(self, globina: int = 0):
        self.l.print(globina)
        print(globina * "  " + ",")
        self.r.print(globina)

    def compile(self) -> str:
        return (
            f"{self.l.compile()}"
            f"{self.r.compile()}"
        )

class Okvir(Vozlišče):
    zaporedje: Zaporedje
    st_spr: int

    def __init__(self, zaporedje: Zaporedje, st_spr: int):
        self.zaporedje = zaporedje
        self.st_spr = st_spr

    def print(self, globina: int = 0):
        print(globina * "  " + "{")
        self.zaporedje.print(globina+1)
        print(globina * "  " + "}")

    def compile(self) -> str:
        ukazi = self.zaporedje.compile()
        ukazi += "POP\n" * self.st_spr
        return ukazi

class FunkcijskiKlic(Vozlišče):
    ime: str
    argumenti: list[Izraz]
    ukazi: Okvir

    def __init__(self, ime: str, ukaz: str, argumenti: list[Izraz], ukazi: Vozlišče):
        self.ime = ime
        self.ukaz = ukaz
        self.argumenti = argumenti
        self.ukazi = ukazi

    def print(self, globina: int = 0):
        print(globina * "  " + "{")
        self.zaporedje.print(globina+1)
        print(globina * "  " + "}")

    def compile(self) -> str:
        ukazi = ""
        for argument in self.argumenti:
            ukazi += argument.compile()
        ukazi += self.ukaz + '\n'
        ukazi += "POP\n" * len(self.argumenti)

        return ukazi

class Print(Vozlišče):
    izrazi: list[Izraz]

    def __init__(self, izrazi: list[Izraz]):
        self.izrazi = izrazi

    def print(self, globina: int = 0):
        print(globina * "  " + "print(")
        for izraz in self.izrazi[:-1]:
            izraz.print(globina + 1)
            print(",")
        self.izrazi[-1].print(globina + 1)
        print(globina * "  " + ")")

    def compile(self) -> str:
        ukazi = ""
        for izraz in self.izrazi:
            ukazi += izraz.compile()
            ukazi += "PRINT\n"
            ukazi += "POP\n"
        return ukazi
