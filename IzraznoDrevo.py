from abc import ABC, abstractmethod
from typing import TypeVar

TVozlišče = TypeVar("TVozlišče", bound="Vozlišče")
TIzraz = TypeVar("TIzraz", bound="Izraz")

class Vozlišče(ABC):

    @abstractmethod
    def drevo(self, globina: int = 0):
        pass

    @abstractmethod
    def optimiziran(self) -> TVozlišče:
        pass

    @abstractmethod
    def prevedi(self) -> str:
        pass

class Izraz(Vozlišče):
    l: TIzraz
    r: TIzraz

    def __init__(self, l: TIzraz, r: TIzraz):
        self.l = l
        self.r = r

    def optimiziran(self) -> TIzraz:
        return Izraz(self.l.optimiziran(), self.r.optimiziran())

class Prazno(Vozlišče):
    def drevo(self, globina: int = 0):
        return globina * "  " + "()\n"

    def prevedi(self) -> str:
        return ""

class Niz(Vozlišče):
    niz: str

    def __init__(self, niz: str):
        self.niz = niz

    def drevo(self, globina: int = 0):
        return globina * "  " + f'"{self.niz}"\n'

    def optimiziran(self) -> TVozlišče:
        return Niz(self.niz)

    def prevedi(self) -> str:
        return f'PUSH "{self.niz}"\n'

class Število(Vozlišče):
    število: float

    def __init__(self, število: float):
        self.število = število

    def drevo(self, globina: int = 0):
        return globina * "  " + str(self.število) + '\n'

    def optimiziran(self) -> TVozlišče:
        return Število(self.število)

    def prevedi(self) -> str:
        return f"PUSH #{self.število}\n"

class Spremenljivka(Vozlišče):
    ime: str
    naslov: int

    def __init__(self, ime: str, naslov: int = None):
        self.ime = ime
        self.naslov = naslov

    def drevo(self, globina: int = 0):
        return globina * "  " + f"{self.ime} @{self.naslov}\n"

    def optimiziran(self) -> TVozlišče:
        return Spremenljivka(self.ime, self.naslov)

    def prevedi(self) -> str:
        return f"PUSH @{self.naslov}\n"

class Potenca(Izraz):
    def drevo(self, globina: int = 0):
        drev  = globina * "  " + "^\n"
        drev += self.l.drevo(globina + 1)
        drev += self.r.drevo(globina + 1)
        return drev

    def optimiziran(self) -> TIzraz:
        l_optimiziran = self.l.optimiziran()
        r_optimiziran = self.r.optimiziran()
        if type(l_optimiziran) == Število and type(r_optimiziran) == Število:
            return Število(l_optimiziran.število ** r_optimiziran.število)
        return Potenca(self.l.optimiziran(), self.r.optimiziran())

    def prevedi(self) -> str:
        return (
            f"{self.l.prevedi()}"
            f"{self.r.prevedi()}"
             "POW\n"
        )

class Množenje(Izraz):
    def drevo(self, globina: int = 0):
        drev  = globina * "  " + "*\n"
        drev += self.l.drevo(globina + 1)
        drev += self.r.drevo(globina + 1)
        return drev

    def optimiziran(self) -> TIzraz:
        l_optimiziran = self.l.optimiziran()
        r_optimiziran = self.r.optimiziran()
        if type(l_optimiziran) == Število and type(r_optimiziran) == Število:
            return Število(l_optimiziran.število * r_optimiziran.število)
        return Množenje(self.l.optimiziran(), self.r.optimiziran())

    def prevedi(self) -> str:
        return (
            f"{self.l.prevedi()}"
            f"{self.r.prevedi()}"
             "MUL\n"
        )

class Deljenje(Izraz):
    def drevo(self, globina: int = 0):
        drev  = globina * "  " + "/\n"
        drev += self.l.drevo(globina + 1)
        drev += self.r.drevo(globina + 1)
        return drev

    def optimiziran(self) -> TIzraz:
        l_optimiziran = self.l.optimiziran()
        r_optimiziran = self.r.optimiziran()
        if type(l_optimiziran) == Število and type(r_optimiziran) == Število:
            return Število(l_optimiziran.število / r_optimiziran.število)
        return Deljenje(self.l.optimiziran(), self.r.optimiziran())

    def prevedi(self) -> str:
        return (
            f"{self.l.prevedi()}"
            f"{self.r.prevedi()}"
             "DIV\n"
        )

class Modulo(Izraz):
    def drevo(self, globina: int = 0):
        drev  = globina * "  " + "%\n"
        drev += self.l.drevo(globina + 1)
        drev += self.r.drevo(globina + 1)
        return drev

    def optimiziran(self) -> TIzraz:
        l_optimiziran = self.l.optimiziran()
        r_optimiziran = self.r.optimiziran()
        if type(l_optimiziran) == Število and type(r_optimiziran) == Število:
            return Število(l_optimiziran.število % r_optimiziran.število)
        return Modulo(self.l.optimiziran(), self.r.optimiziran())

    def prevedi(self) -> str:
        return (
            f"{self.l.prevedi()}"
            f"{self.r.prevedi()}"
             "MOD\n"
        )

class Seštevanje(Izraz):
    def drevo(self, globina: int = 0):
        drev  = globina * "  " + "+\n"
        drev += self.l.drevo(globina + 1)
        drev += self.r.drevo(globina + 1)
        return drev

    def optimiziran(self) -> TIzraz:
        l_optimiziran = self.l.optimiziran()
        r_optimiziran = self.r.optimiziran()
        if type(l_optimiziran) == Število and type(r_optimiziran) == Število:
            return Število(l_optimiziran.število + r_optimiziran.število)
        return Seštevanje(self.l.optimiziran(), self.r.optimiziran())

    def prevedi(self) -> str:
        return (
            f"{self.l.prevedi()}"
            f"{self.r.prevedi()}"
             "ADD\n"
        )

class Odštevanje(Izraz):
    def drevo(self, globina: int = 0):
        drev  = globina * "  " + "-\n"
        drev += self.l.drevo(globina + 1)
        drev += self.r.drevo(globina + 1)
        return drev

    def optimiziran(self) -> TIzraz:
        l_optimiziran = self.l.optimiziran()
        r_optimiziran = self.r.optimiziran()
        if type(l_optimiziran) == Število and type(r_optimiziran) == Število:
            return Število(l_optimiziran.število - r_optimiziran.število)
        return Odštevanje(self.l.optimiziran(), self.r.optimiziran())

    def prevedi(self,) -> str:
        return (
            f"{self.l.prevedi()}"
            f"{self.r.prevedi()}"
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

    def drevo(self, globina: int = 0):
        drev  = globina * "  " + self.spremenljivka.drevo()[:-1] + " =\n"
        drev += self.izraz.drevo(globina + 1)
        return drev

    def optimiziran(self) -> TIzraz:
        return Priredba(self.spremenljivka, self.izraz.optimiziran(), self.nova_spr)

    def prevedi(self) -> str:
        stavki = self.izraz.prevedi()
        if not self.nova_spr:
            stavki += (
                f"MOV @{self.spremenljivka.naslov}\n"
                 "POP\n"
            )
        return stavki

class Zaporedje(Izraz):
    def __init__(self, zaporedje: Izraz, priredba: Priredba):
        self.l = zaporedje
        self.r = priredba

    def drevo(self, globina: int = 0):
        drev  = self.l.drevo(globina)
        drev += globina * "  " + ",\n"
        drev += self.r.drevo(globina)
        return drev

    def optimiziran(self) -> TIzraz:
        return Zaporedje(self.l.optimiziran(), self.r.optimiziran())

    def prevedi(self) -> str:
        return (
            f"{self.l.prevedi()}"
            f"{self.r.prevedi()}"
        )

class Okvir(Vozlišče):
    zaporedje: Zaporedje
    st_spr: int

    def __init__(self, zaporedje: Zaporedje, st_spr: int):
        self.zaporedje = zaporedje
        self.st_spr = st_spr

    def drevo(self, globina: int = 0):
        drev  = globina * "  " + "{\n"
        drev += self.zaporedje.drevo(globina+1)
        drev += globina * "  " + "}\n"
        return drev

    def optimiziran(self) -> TVozlišče:
        return Okvir(self.zaporedje.optimiziran(), self.st_spr)

    def prevedi(self) -> str:
        ukazi = self.zaporedje.prevedi()
        ukazi += "POP\n" * self.st_spr
        return ukazi

class FunkcijskiKlic(Vozlišče):
    ime: str
    argumenti: list[Izraz]
    okvir: Okvir

    def __init__(self, ime: str, argumenti: list[Izraz], ukazi: Vozlišče):
        self.ime = ime
        self.argumenti = argumenti
        self.okvir = ukazi

    def drevo(self, globina: int = 0):
        drev  = globina * "  " + "{\n"
        drev += self.zaporedje.drevo(globina+1)
        drev += globina * "  " + "}\n"
        return drev

    def optimiziran(self) -> TVozlišče:
        return FunkcijskiKlic(self.ime, [ arg.optimiziran() for arg in self.argumenti ], self.okvir.optimiziran())

    def prevedi(self) -> str:
        ukazi = ""
        for argument in self.argumenti:
            ukazi += argument.prevedi()
        ukazi += self.ukaz + '\n'
        ukazi += "POP\n" * len(self.argumenti)

        return ukazi

class Print(Vozlišče):
    izrazi: list[Izraz]

    def __init__(self, izrazi: list[Izraz]):
        self.izrazi = izrazi

    def drevo(self, globina: int = 0):
        drev  = globina * "  " + "print(\n"
        for izraz in self.izrazi[:-1]:
            drev += izraz.drevo(globina + 1)
            drev += ",\n"
        drev += self.izrazi[-1].drevo(globina + 1)
        drev += globina * "  " + ")\n"
        return drev

    def optimiziran(self) -> TVozlišče:
        return Print([ iz.optimiziran() for iz in self.izrazi ])

    def prevedi(self) -> str:
        ukazi = ""
        for izraz in self.izrazi:
            ukazi += izraz.prevedi()
            ukazi += "PRINT\n"
            ukazi += "POP\n"
        return ukazi
