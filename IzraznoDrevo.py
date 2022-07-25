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

    def __eq__(self, __o: TIzraz) -> bool:
        return type(self) == type(__o) and self.l == __o.l and self.r == __o.r

class Prazno(Vozlišče):
    def __eq__(self, __o: object) -> bool:
        return type(self) is Prazno and type(__o) is Prazno

    def drevo(self, globina: int = 0):
        return globina * "  " + "()\n"

    def prevedi(self) -> str:
        return ""

class Niz(Vozlišče):
    niz: str

    def __init__(self, niz: str):
        self.niz = niz

    def __str__(self) -> str:
        return self.niz

    def __eq__(self, __o: object) -> bool:
        return type(self) == type(__o) and self.niz == __o.niz

    def __add__(self, o: object):
        return self.niz + o.niz

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

    def __str__(self) -> str:
        return str(self.število)

    def __eq__(self, __o: bool) -> bool:
        return type(self) == type(__o) and self.število == __o.število

    def __add__(self, o: object):
        return Število(self.število + o.število)

    def __sub__(self, o: object):
        return Število(self.število - o.število)

    def __mul__(self, o: object):
        return Število(self.število * o.število)

    def __truediv__(self, o: object):
        return Število(self.število / o.število)

    def __pow__(self, o: object):
        return Število(self.število ** o.število)

    def __mod__(self, o: object):
        return Število(self.število % o.število)

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

    def __str__(self) -> str:
        return f"{self.ime} @{self.naslov}"

    def __eq__(self, __o: object) -> bool:
        return (
            type(self) == type(__o) 
            and self.ime == __o.ime
            and self.naslov == __o.naslov
        )

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
        opti = Potenca(self.l.optimiziran(), self.r.optimiziran())

        if type(opti.l) is Število and type(opti.r) is Število:
            print(f"OPTI {opti.l} ^ {opti.r}", end="")
            opti = opti.l ** opti.r
            print(f" -> {opti}")

        return opti

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
        opti = Množenje(self.l.optimiziran(), self.r.optimiziran())

        if opti.l == opti.r:
            print("OPTI x * x -> x^2")
            opti = Potenca(opti.l, Število(2.0))
        elif type(opti.l) is Število and type(opti.r) is Število:
            print(f"OPTI {opti.l} * {opti.r}", end="")
            opti = Število(opti.l.število * opti.r.število)
            print(f" -> {opti}")

        elif type(opti.l) == Množenje and type(opti.r) is Število:
            b = opti.r
            if type(opti.l.l) is Število:
                a = opti.l.l; x = opti.l.r
                print(f"OPTI ({a} * x) * {b} -> {a * b} * x")
                opti = Množenje(a * b, x)
            elif type(opti.l.r) is Število:
                x = opti.l.l; a = opti.l.r
                print(f"OPTI (x * {a}) * {b} -> x * {a * b}")
                opti = Množenje(x, a * b)
        elif type(opti.l) is Število and type(opti.r) == Množenje:
            a = opti.l
            if type(opti.r.l) is Število:
                b = opti.r.l; x = opti.r.r
                print(f"OPTI {a} * ({b} * x) -> {a * b} * x")
                opti = Množenje(x, b * a)
            elif type(opti.r.r) is Število:
                x = opti.r.l; b = opti.r.r
                print(f"OPTI {a} * (x * {b}) -> x * {a * b}")
                opti = Množenje(a * b, x)

        return opti

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
        opti = Deljenje(self.l.optimiziran(), self.r.optimiziran())

        if opti.l == opti.r:
            print("OPTI x / x -> 1.0")
            opti = Število(1.0)
        elif type(opti.l) is Število and type(opti.r) is Število:
            if opti.l.število == 0.0:
                print(f"OPTI {opti.l} / {opti.r} -> 0.0")
                opti = Število(0.0)
            elif opti.r.število == 0.0:
                if opti.l.število > 0.0:
                    print(f"OPTI {opti.l} / {opti.r} -> inf")
                    opti = Število(float("inf"))
                else:
                    print(f"OPTI {opti.l} / {opti.r} -> -inf")
                    opti = Število(float("-inf"))
            else:
                opti = opti.l / opti.r

        elif type(opti.l) == Deljenje and type(opti.r) is Število:
            b = opti.r
            if type(opti.l.l) is Število:
                a = opti.l.l; x = opti.l.r
                print(f"OPTI ({a} / x) / {b} -> {a / b} / x")
                opti = Deljenje(a / b, x)
            elif type(opti.l.r) is Število:
                x = opti.l.l; a = opti.l.r
                print(f"OPTI (x / {a}) / {b} -> x / {a * b}")
                opti = Deljenje(x, a * b)
        elif type(opti.l) is Število and type(opti.r) == Deljenje:
            a = opti.l
            if type(opti.r.l) is Število:
                b = opti.r.l; x = opti.r.r
                print(f"OPTI {a} / ({b} / x) -> {a / b} * x")
                opti = Množenje(a / b, x)
            elif type(opti.r.r) is Število:
                x = opti.r.l; b = opti.r.r
                print(f"OPTI {a} / (x / {b}) -> {a * b} / x")
                opti = Deljenje(a * b, x)

        return opti

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
        opti = Modulo(self.l.optimiziran(), self.r.optimiziran())

        if opti.l == opti.r:
            print("OPTI x % x -> 1.0")
            opti = Število(1.0)
        elif type(opti.l) is Število and type(opti.r) is Število:
            print(f"OPTI {opti.l} % {opti.r} -> {opti.l % opti.r}")
            opti = opti.l % opti.r
            
        elif type(opti.l) is Modulo and type(opti.r) is Število:
            if type(opti.l.r) is Število and opti.l.r == opti.r:
                n = opti.r
                print(f"OPTI (x % {n}) % {n} -> x % {n}")
                opti = Modulo(opti.l.l, opti.r)
        elif type(opti.r) is Število:
            n = opti.r
            if type(opti.l) is Seštevanje:
                if type(opti.l.l) is Modulo and type(opti.l.r) is Modulo:
                    if opti.l.l.r == opti.l.r.r == opti.r:
                        x = opti.l.l.l; y = opti.l.r.l; n = opti.r
                        print(f"OPTI ((x % {n}) + (y % {n})) % {n} -> (x + y) % {n}")
                        opti = Modulo(Seštevanje(x, y), n)
            elif type(opti.l) is Množenje:
                if type(opti.l.l) is Modulo and type(opti.l.r) is Modulo:
                    if opti.l.l.r == opti.l.r.r == opti.r:
                        x = opti.l.l.l; y = opti.l.r.l; n = opti.r
                        print(f"OPTI ((x % {n}) * (y % {n})) % {n} -> (x * y) % {n}")
                        opti = Modulo(Množenje(x, y), n)

        return opti

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
        opti = Seštevanje(self.l.optimiziran(), self.r.optimiziran())

        if opti.l == opti.r:
            print("OPTI x + x -> 2.0 * x")
            opti = Množenje(Število(2.0), opti.l)
        elif type(opti.l) is Število and type(opti.r) is Število:
            print(f"OPTI {opti.l} + {opti.r}", end="")
            opti = opti.l + opti.r
            print(f" -> {opti}")

        elif type(opti.l) == Seštevanje and type(opti.r) is Število:
            b = opti.r
            if type(opti.l.l) is Število:
                a = opti.l.l; x = opti.l.r
                print(f"OPTI ({a} + x) + {b} -> {a + b} + x")
                opti = Seštevanje(a + b, x)
            elif type(opti.l.r) is Število:
                x = opti.l.l; a = opti.l.r
                print(f"OPTI (x + {a}) + {b} -> x + {a + b}")
                opti = Seštevanje(x, a + b)
        elif type(opti.l) is Število and type(opti.r) == Seštevanje:
            a = opti.l
            if type(opti.r.l) is Število:
                b = opti.r.l; x = opti.r.r
                print(f"OPTI {a} + ({b} + x) -> {b + a} + x")
                opti = Seštevanje(b + a, x)
            elif type(opti.r.r) is Število:
                x = opti.r.l; b = opti.r.r
                print(f"OPTI {a} + (x + {b}) -> x + {a + b}")
                opti = Seštevanje(x, a + b)

        return opti

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
        opti = Odštevanje(self.l.optimiziran(), self.r.optimiziran())

        if opti.l == opti.r:
            print("OPTI x - x -> 0.0")
            opti = Število(0.0)
        elif type(opti.l) is Število and type(opti.r) is Število:
            print(f"OPTI {opti.l} - {opti.r}", end="")
            opti = opti.l - opti.r
            print(f" -> {opti}")

        elif type(opti.l) == Odštevanje and type(opti.r) is Število:
            b = opti.r
            if type(opti.l.l) is Število:
                a = opti.l.l; x = opti.l.r
                print(f"OPTI ({a} - x) - {b} -> {a - b} - x")
                opti = Odštevanje(a - b, x)
            elif type(opti.l.r) is Število:
                x = opti.l.l; a = opti.l.r
                print(f"OPTI (x - {a}) - {b} -> x - {a + b}")
                opti = Odštevanje(x, a + b)
        elif type(opti.l) is Število and type(opti.r) == Odštevanje:
            a = opti.l
            if type(opti.r.l) is Število:
                b = opti.r.l; x = opti.r.r
                print(f"OPTI {a} - ({b} - x) -> x - {b - a}")
                opti = Odštevanje(x, b - a)
            elif type(opti.r.r) is Število:
                x = opti.r.l; b = opti.r.r
                print(f"OPTI {a} - (x - {b}) -> {a + b} - x")
                opti = Odštevanje(a + b, x)

        return opti

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

    def __eq__(self, __o: object) -> bool:
        return (
            self.spremenljivka == __o.spremenljivka
            and self.izraz == __o.izraz
            and self.nova_spr == __o.nova_spr
        )

    def drevo(self, globina: int = 0):
        drev  = globina * "  " + self.spremenljivka.drevo()[:-1] + " =\n"
        drev += self.izraz.drevo(globina + 1)
        return drev

    def optimiziran(self) -> TIzraz:
        opti = Priredba(self.spremenljivka, self.izraz.optimiziran(), self.nova_spr)
        return opti

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
        opti = Zaporedje(self.l.optimiziran(), self.r.optimiziran())
        return opti

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

    def __eq__(self, __o: object) -> bool:
        return type(__o) is Okvir and self.zaporedje == __o.zaporedje

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
        return FunkcijskiKlic(
            self.ime, 
            [ arg.optimiziran() for arg in self.argumenti ], 
            self.okvir.optimiziran()
        )

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

    def __eq__(self, __o: object) -> bool:
        return (
            len(self.izrazi) == len(__o.izrazi) 
            and all(iz1 == iz2 for iz1, iz2 in zip(self.izrazi, __o.izrazi))
        )

    def drevo(self, globina: int = 0):
        drev  = globina * "  " + "print(\n"
        for izraz in self.izrazi[:-1]:
            drev += izraz.drevo(globina + 1)
            drev += (globina + 1) * "  " + ",\n"
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
