from abc import ABC, abstractmethod
from math import ceil
from typing import TypeVar

TVozlišče = TypeVar("TVozlišče", bound="Vozlišče")
TIzraz = TypeVar("TIzraz", bound="Izraz")

class Vozlišče(ABC):

    @abstractmethod
    def drevo(self, globina: int = 0) -> str:
        pass

    @abstractmethod
    def optimiziran(self, nivo: int = 0) -> TVozlišče:
        pass

    @abstractmethod
    def prevedi(self) -> str:
        pass

    @abstractmethod
    def __len__(self) -> int:
        pass

class Izraz(Vozlišče):
    l: TIzraz
    r: TIzraz

    def __init__(self, l: TIzraz, r: TIzraz):
        self.l = l
        self.r = r

    def __len__(self) -> int:
        return 1

    def __eq__(self, o: TIzraz) -> bool:
        return type(self) == type(o) and self.l == o.l and self.r == o.r

class Prazno(Vozlišče):
    def __len__(self) -> int:
        return 0

    def __str__(self) -> str:
        return "()"

    def __eq__(self, o: object) -> bool:
        return type(o) is Prazno

    def drevo(self, globina: int = 0) -> str:
        return globina * "  " + f"{self}\n"

    def optimiziran(self, _: int = 0) -> TVozlišče:
        return Prazno()

    def prevedi(self) -> str:
        return ""

class Niz(Vozlišče):
    niz: str

    def __init__(self, niz: str):
        niz = str(niz)
        niz = niz.replace('\\n', '\n')
        niz = niz.replace('\\r', '\r')
        niz = niz.replace('\\t', '\t')
        self.niz = niz

    def __len__(self) -> int:
        return ceil(len(self.niz) / 4)

    def __str__(self) -> str:
        niz = self.niz
        niz = niz.replace('\n', '\\n')
        niz = niz.replace('\r', '\\r')
        niz = niz.replace('\t', '\\t')
        return niz

    def __eq__(self, o: object) -> bool:
        return type(o) is Niz and self.niz == o.niz

    def __add__(self, o: object):
        return Niz(self.niz + str(o))

    def __mul__(self, o: object):
        return Niz(self.niz * int(o))

    def drevo(self, globina: int = 0) -> str:
        return globina * "  " + f'"{self}"\n'

    def optimiziran(self, _: int = 0) -> TVozlišče:
        return Niz(self.niz)

    def prevedi(self) -> str:
        ostanek = len(self.niz) % 4
        ukazi = ""

        if ostanek > 0:
            string = self.niz[-ostanek:]
            string = string.replace('\n', '\\n')
            string = string.replace('\r', '\\r')
            string = string.replace('\t', '\\t')
            ukazi += f'PUSH "{string}"\n'

        start = len(self.niz) - ostanek - 4

        for i in range(start, -1, -4):
            string = self.niz[i:i+4]
            string = string.replace('\n', '\\n')
            string = string.replace('\r', '\\r')
            string = string.replace('\t', '\\t')
            ukazi += f'PUSH "{string}"\n'
        
        return ukazi

class Število(Vozlišče):
    število: float

    def __init__(self, število: float):
        self.število = float(število)

    def __len__(self) -> int:
        return 1

    def __str__(self) -> str:
        return str(self.število)

    def __float__(self) -> int:
        return self.število

    def __int__(self) -> int:
        return int(self.število)

    def __eq__(self, o: object) -> bool:
        return type(o) is Število and self.število == o.število

    def __gt__(self, o: object) -> bool:
        return type(o) == Število and self.število > o.število

    def __lt__(self, o: object) -> bool:
        return type(o) == Število and self.število < o.število

    def __add__(self, o: object):
        if type(o) == Niz:
            return Niz(o.niz * int(self.število))
        return Število(self.število + float(o))

    def __sub__(self, o: object):
        return Število(self.število - float(o))

    def __mul__(self, o: object):
        return Število(self.število * float(o))

    def __truediv__(self, o: object):
        return Število(self.število / float(o))

    def __pow__(self, o: object):
        return Število(self.število ** float(o))

    def __mod__(self, o: object):
        return Število(self.število % float(o))

    def drevo(self, globina: int = 0) -> str:
        return globina * "  " + str(self.število) + '\n'

    def optimiziran(self, _: int = 0) -> TVozlišče:
        return Število(self.število)

    def prevedi(self) -> str:
        return f"PUSH #{self.število}\n"

class Spremenljivka(Vozlišče):
    ime: str
    naslov: int

    def __init__(self, ime: str, naslov: int):
        self.ime = str(ime)
        self.naslov = int(naslov)

    def __len__(self) -> int:
        return 1

    def __str__(self) -> str:
        return f"{self.ime} @{self.naslov}"

    def __eq__(self, o: object) -> bool:
        return (
            type(self) is type(o) 
            and self.ime == o.ime
            and self.naslov == o.naslov
        )

    def drevo(self, globina: int = 0) -> str:
        return globina * "  " + f"{self}\n"

    def optimiziran(self, _: int = 0) -> TVozlišče:
        return Spremenljivka(self.ime, self.naslov)

    def prevedi(self) -> str:
        return f"PUSH @{self.naslov}\n"

class Resnica(Vozlišče):
    def __eq__(self, __o: object) -> bool:
        return type(__o) is Resnica

    def __len__(self) -> int:
        return 1

    def __str__(self) -> str:
        return "resnica"

    def drevo(self, globina: int = 0) -> str:
        return globina * "  " + "resnica\n"

    def optimiziran(self, nivo: int = 0) -> TVozlišče:
        return Resnica()

    def prevedi(self) -> str:
        return Število(1).prevedi()

class Laž(Vozlišče):
    def __eq__(self, __o: object) -> bool:
        return type(__o) is Laž

    def __len__(self) -> int:
        return 1

    def __str__(self) -> str:
        return "laž"

    def drevo(self, globina: int = 0) -> str:
        return globina * "  " + "laž\n"

    def optimiziran(self, nivo: int = 0) -> TVozlišče:
        return Laž()

    def prevedi(self) -> str:
        return Število(0).prevedi()

class Seštevanje(Izraz):
    def drevo(self, globina: int = 0) -> str:
        return (
            globina * "  " + "+\n" +
            self.l.drevo(globina + 1) +
            self.r.drevo(globina + 1)
        )

    def optimiziran(self, nivo: int = 0) -> TIzraz:
        opti = Seštevanje(self.l.optimiziran(nivo), self.r.optimiziran(nivo))
        
        if type(opti.l) is Niz and type(opti.r) in [Niz, Število]:
            print(f'MAKE "{opti.l}" + "{opti.r}" -> "{opti.l + opti.r}"')
            return opti.l + opti.r

        if nivo == 0: return opti

        if opti.l == opti.r:
            print("OPTI x + x -> 2.0 * x")
            return Množenje(Število(2.0), opti.l)
        elif type(opti.l) in [Število, Niz] and type(opti.r) in [Število, Niz]:
            print(f"OPTI {opti.l} + {opti.r} -> {opti.l + opti.r}")
            return opti.l + opti.r

        if nivo == 1: return opti

        if type(opti.l) == Seštevanje and type(opti.r) is Število:
            b = opti.r
            if type(opti.l.l) is Število:
                a = opti.l.l; x = opti.l.r
                print(f"OPTI ({a} + x) + {b} -> {a + b} + x")
                return Seštevanje(a + b, x)
            elif type(opti.l.r) is Število:
                x = opti.l.l; a = opti.l.r
                print(f"OPTI (x + {a}) + {b} -> x + {a + b}")
                return Seštevanje(x, a + b)
        if type(opti.l) is Število and type(opti.r) == Seštevanje:
            a = opti.l
            if type(opti.r.l) is Število:
                b = opti.r.l; x = opti.r.r
                print(f"OPTI {a} + ({b} + x) -> {b + a} + x")
                return Seštevanje(b + a, x)
            elif type(opti.r.r) is Število:
                x = opti.r.l; b = opti.r.r
                print(f"OPTI {a} + (x + {b}) -> x + {a + b}")
                return Seštevanje(x, a + b)

        return opti

    def prevedi(self) -> str:
        return (
            self.l.prevedi() +
            self.r.prevedi() +
            "ADD\n"
        )

class Odštevanje(Izraz):
    def drevo(self, globina: int = 0) -> str:
        return (
            globina * "  " + "-\n" +
            self.l.drevo(globina + 1) +
            self.r.drevo(globina + 1)
        )

    def optimiziran(self, nivo: int = 0) -> TIzraz:
        opti = Odštevanje(self.l.optimiziran(nivo), self.r.optimiziran(nivo))

        if nivo == 0: return opti

        if opti.l == opti.r:
            print("OPTI x - x -> 0.0")
            return Število(0.0)
        elif type(opti.l) is Število and type(opti.r) is Število:
            print(f"OPTI {opti.l} - {opti.r} -> {opti.l - opti.r}")
            return opti.l - opti.r

        if nivo == 1: return opti

        if type(opti.l) == Odštevanje and type(opti.r) is Število:
            b = opti.r
            if type(opti.l.l) is Število:
                a = opti.l.l; x = opti.l.r
                print(f"OPTI ({a} - x) - {b} -> {a - b} - x")
                return Odštevanje(a - b, x)
            elif type(opti.l.r) is Število:
                x = opti.l.l; a = opti.l.r
                print(f"OPTI (x - {a}) - {b} -> x - {a + b}")
                return Odštevanje(x, a + b)
        elif type(opti.l) is Število and type(opti.r) == Odštevanje:
            a = opti.l
            if type(opti.r.l) is Število:
                b = opti.r.l; x = opti.r.r
                print(f"OPTI {a} - ({b} - x) -> x - {b - a}")
                return Odštevanje(x, b - a)
            elif type(opti.r.r) is Število:
                x = opti.r.l; b = opti.r.r
                print(f"OPTI {a} - (x - {b}) -> {a + b} - x")
                return Odštevanje(a + b, x)

        return opti

    def prevedi(self) -> str:
        return (
            self.l.prevedi() +
            self.r.prevedi() +
            "SUB\n"
        )

class Množenje(Izraz):
    def drevo(self, globina: int = 0) -> str:
        return (
            globina * "  " + "*\n" +
            self.l.drevo(globina + 1) +
            self.r.drevo(globina + 1)
        )

    def optimiziran(self, nivo: int = 0) -> TIzraz:
        opti = Množenje(self.l.optimiziran(nivo), self.r.optimiziran(nivo))

        if type(opti.l) is Niz and type(opti.r) is Število:
            print(f'MAKE "{opti.l}" * {opti.r} -> "{opti.l * opti.r}"')
            return opti.l * opti.r
        elif type(opti.l) is Število and type(opti.r) is Niz:
            print(f'MAKE {opti.l} * "{opti.r}" -> "{opti.l * opti.r}"')
            return opti.l * opti.r

        if nivo == 0: return opti

        if opti.l == opti.r:
            print("OPTI x * x -> x^2")
            return Potenca(opti.l, Število(2.0))
        elif type(opti.l) in [Število, Niz] and type(opti.r) in [Število, Niz]:
            print(f"OPTI {opti.l} * {opti.r} -> {opti.l + opti.r}")
            return opti.l * opti.r

        if nivo == 1: return opti

        if type(opti.l) == Množenje and type(opti.r) is Število:
            b = opti.r
            if type(opti.l.l) is Število:
                a = opti.l.l; x = opti.l.r
                print(f"OPTI ({a} * x) * {b} -> {a * b} * x")
                return Množenje(a * b, x)
            elif type(opti.l.r) is Število:
                x = opti.l.l; a = opti.l.r
                print(f"OPTI (x * {a}) * {b} -> x * {a * b}")
                return Množenje(x, a * b)
        elif type(opti.l) is Število and type(opti.r) == Množenje:
            a = opti.l
            if type(opti.r.l) is Število:
                b = opti.r.l; x = opti.r.r
                print(f"OPTI {a} * ({b} * x) -> {a * b} * x")
                return Množenje(x, b * a)
            elif type(opti.r.r) is Število:
                x = opti.r.l; b = opti.r.r
                print(f"OPTI {a} * (x * {b}) -> x * {a * b}")
                return Množenje(a * b, x)

        return opti

    def prevedi(self) -> str:
        return (
            self.l.prevedi() +
            self.r.prevedi() +
            "MUL\n"
        )

class Deljenje(Izraz):
    def drevo(self, globina: int = 0) -> str:
        return (
            globina * "  " + "/\n" +
            self.l.drevo(globina + 1) +
            self.r.drevo(globina + 1)
        )

    def optimiziran(self, nivo: int = 0) -> TIzraz:
        opti = Deljenje(self.l.optimiziran(nivo), self.r.optimiziran(nivo))

        if nivo == 0: return opti

        if opti.l == opti.r:
            print("OPTI x / x -> 1.0")
            return Število(1.0)
        elif type(opti.l) is Število and type(opti.r) is Število:
            if opti.l.število == 0.0:
                print(f"OPTI {opti.l} / {opti.r} -> 0.0")
                return Število(0.0)
            elif opti.r.število == 0.0:
                if opti.l.število > 0.0:
                    print(f"OPTI {opti.l} / {opti.r} -> inf")
                    return Število(float("inf"))
                else:
                    print(f"OPTI {opti.l} / {opti.r} -> -inf")
                    return Število(float("-inf"))
            else:
                return opti.l / opti.r

        if nivo == 1: return opti

        if type(opti.l) == Deljenje and type(opti.r) is Število:
            b = opti.r
            if type(opti.l.l) is Število:
                a = opti.l.l; x = opti.l.r
                print(f"OPTI ({a} / x) / {b} -> {a / b} / x")
                return Deljenje(a / b, x)
            elif type(opti.l.r) is Število:
                x = opti.l.l; a = opti.l.r
                print(f"OPTI (x / {a}) / {b} -> x / {a * b}")
                return Deljenje(x, a * b)
        elif type(opti.l) is Število and type(opti.r) == Deljenje:
            a = opti.l
            if type(opti.r.l) is Število:
                b = opti.r.l; x = opti.r.r
                print(f"OPTI {a} / ({b} / x) -> {a / b} * x")
                return Množenje(a / b, x)
            elif type(opti.r.r) is Število:
                x = opti.r.l; b = opti.r.r
                print(f"OPTI {a} / (x / {b}) -> {a * b} / x")
                return Deljenje(a * b, x)

        return opti

    def prevedi(self) -> str:
        return (
            self.l.prevedi() +
            self.r.prevedi() +
            "DIV\n"
        )

class Modulo(Izraz):
    def drevo(self, globina: int = 0) -> str:
        return (
            globina * "  " + "%\n" +
            self.l.drevo(globina + 1) +
            self.r.drevo(globina + 1)
        )

    def optimiziran(self, nivo: int = 0) -> TIzraz:
        opti = Modulo(self.l.optimiziran(nivo), self.r.optimiziran(nivo))

        if nivo == 0: return opti

        if opti.l == opti.r:
            print("OPTI x % x -> 1.0")
            return Število(1.0)
        elif type(opti.l) is Število and type(opti.r) is Število:
            print(f"OPTI {opti.l} % {opti.r} -> {opti.l % opti.r}")
            return opti.l % opti.r

        if nivo == 1: return opti

        if type(opti.l) is Modulo and type(opti.r) is Število:
            if type(opti.l.r) is Število and opti.l.r == opti.r:
                n = opti.r
                print(f"OPTI (x % {n}) % {n} -> x % {n}")
                return Modulo(opti.l.l, opti.r)
        elif type(opti.r) is Število:
            n = opti.r
            if type(opti.l) is Seštevanje:
                if type(opti.l.l) is Modulo and type(opti.l.r) is Modulo:
                    if opti.l.l.r == opti.l.r.r == opti.r:
                        x = opti.l.l.l; y = opti.l.r.l; n = opti.r
                        print(f"OPTI ((x % {n}) + (y % {n})) % {n} -> (x + y) % {n}")
                        return Modulo(Seštevanje(x, y), n)
            elif type(opti.l) is Množenje:
                if type(opti.l.l) is Modulo and type(opti.l.r) is Modulo:
                    if opti.l.l.r == opti.l.r.r == opti.r:
                        x = opti.l.l.l; y = opti.l.r.l; n = opti.r
                        print(f"OPTI ((x % {n}) * (y % {n})) % {n} -> (x * y) % {n}")
                        return Modulo(Množenje(x, y), n)

        return opti

    def prevedi(self) -> str:
        return (
            self.l.prevedi() +
            self.r.prevedi() +
            "MOD\n"
        )

class Potenca(Izraz):
    def drevo(self, globina: int = 0) -> str:
        return (
            globina * "  " + "^\n" +
            self.l.drevo(globina + 1) +
            self.r.drevo(globina + 1)
        )

    def optimiziran(self, nivo: int = 0) -> TIzraz:
        opti = Potenca(self.l.optimiziran(nivo), self.r.optimiziran(nivo))

        if nivo == 0: return opti

        if type(opti.l) is Število and type(opti.r) is Število:
            print(f"OPTI {opti.l} ^ {opti.r} -> {opti.l ** opti.r}")
            return opti.l ** opti.r

        return opti

    def prevedi(self) -> str:
        return (
            self.l.prevedi() +
            self.r.prevedi() +
            "POW\n"
        )

class Zanikaj(Vozlišče):
    vozlišče: Vozlišče

    def __init__(self, vozlišče: Vozlišče):
        self.vozlišče = vozlišče

    def __len__(self) -> int:
        return 1

    def drevo(self, globina: int = 0) -> str:
        return (
            globina * "  " + "!\n" +
            self.vozlišče.drevo(globina + 1)
        )

    def optimiziran(self, nivo: int = 0) -> Vozlišče:
        opti = Zanikaj(self.vozlišče.optimiziran(nivo))

        if nivo == 1: return opti

        if type(opti.vozlišče) is Resnica:
            return Laž()
        elif type(opti.vozlišče) == Laž:
            return Resnica()

        if nivo == 2: return opti

        return opti

    def prevedi(self) -> str:
        return Če(self.vozlišče, Laž(), Resnica()).prevedi()

class Konjunkcija(Izraz):
    def __len__(self) -> int:
        return 1

    def drevo(self, globina: int = 0) -> str:
        return (
            globina * "  " + "&\n" +
            self.l.drevo(globina + 1) + 
            self.r.drevo(globina + 1)
        )

    def optimiziran(self, nivo: int = 0) -> TVozlišče:
        opti = Konjunkcija(self.l.optimiziran(nivo), self.r.optimiziran(nivo))

        if nivo == 0: return opti

        if opti.l == Resnica() and opti.r == Resnica():
            return Resnica()
        elif opti.l == Laž() and opti.r == Resnica():
            return Laž()
        elif opti.l == Resnica() and opti.r == Laž():
            return Laž()
        elif opti.l == Laž() or opti.r == Laž():
            return Laž()

        if nivo == 1: return opti

        return opti

    def prevedi(self) -> str:
        return Če(self.l, self.r, Laž()).prevedi()

class Disjunkcija(Izraz):
    def __len__(self) -> int:
        return 1

    def drevo(self, globina: int = 0) -> str:
        return (
            globina * "  " + "|\n" +
            self.l.drevo(globina + 1) + 
            self.r.drevo(globina + 1)
        )

    def optimiziran(self, nivo: int = 0) -> TVozlišče:
        opti = Disjunkcija(self.l.optimiziran(nivo), self.r.optimiziran(nivo))

        if nivo == 0: return opti

        if opti.l == Resnica() and opti.r == Resnica():
            return Resnica()
        elif opti.l == Laž() and opti.r == Resnica():
            return Resnica()
        elif opti.l == Resnica() and opti.r == Laž():
            return Resnica()
        elif opti.l == Laž() or opti.r == Laž():
            return Laž()

        if nivo == 1: return opti

        return opti

    def prevedi(self) -> str:
        return Če(self.l, Resnica(), self.r).prevedi()

class Enako(Izraz):
    def __len__(self) -> int:
        return 1

    def drevo(self, globina: int = 0) -> str:
        return (
            globina * "  " + "==\n" +
            self.l.drevo(globina + 1) + 
            self.r.drevo(globina + 1)
        )

    def optimiziran(self, nivo: int = 0) -> TVozlišče:
        opti = Enako(self.l.optimiziran(nivo), self.r.optimiziran(nivo))

        if nivo == 0: return opti

        if opti.l == opti.r:
            return Resnica()

        if nivo == 1: return opti

        if type(opti.l) is Število and type(opti.r) is Število:
            if opti.l > opti.r:
                return Laž()
            elif opti.l < opti.r:
                return Laž()

        if nivo == 2: return opti

        return opti

    def prevedi(self) -> str:
        razlika = Odštevanje(self.l, self.r).optimiziran(2)
        return (
            razlika.prevedi() +
            "ZERO\n"
        )

class Večje(Izraz):
    def __len__(self) -> int:
        return 1

    def drevo(self, globina: int = 0) -> str:
        return (
            globina * "  " + ">\n" +
            self.l.drevo(globina + 1) + 
            self.r.drevo(globina + 1)
        )

    def optimiziran(self, nivo: int = 0) -> TVozlišče:
        opti = Večje(self.l.optimiziran(nivo), self.r.optimiziran(nivo))

        if nivo == 0: return opti

        if opti.l == opti.r:
            return Laž()

        if nivo == 1: return opti

        if type(opti.l) is Število and type(opti.r) is Število:
            if opti.l > opti.r:
                return Resnica()
            elif opti.l < opti.r:
                return Laž()

        if nivo == 2: return opti

        return opti

    def prevedi(self) -> str:
        razlika = Odštevanje(self.l, self.r).optimiziran(2)
        return (
            razlika.prevedi() +
            "POS\n"
        )

class VečjeEnako(Izraz):
    def __len__(self) -> int:
        return 1

    def drevo(self, globina: int = 0) -> str:
        return (
            globina * "  " + ">=\n" +
            self.l.drevo(globina + 1) + 
            self.r.drevo(globina + 1)
        )

    def optimiziran(self, nivo: int = 0) -> TVozlišče:
        return Disjunkcija(
            Večje(self.l, self.r),
            Enako(self.l, self.r)
        ).optimiziran(nivo)

    def prevedi(self) -> str:
        return self.optimiziran().prevedi()

class Manjše(Izraz):
    def drevo(self, globina: int = 0) -> str:
        return (
            globina * "  " + "<\n" +
            self.l.drevo(globina + 1) + 
            self.r.drevo(globina + 1)
        )

    def optimiziran(self, nivo: int = 0) -> TVozlišče:
        return Večje(
            self.r, 
            self.l
        ).optimiziran(nivo)

    def prevedi(self) -> str:
        return self.optimiziran().prevedi()

class ManjšeEnako(Izraz):
    def __len__(self) -> int:
        return 1

    def drevo(self, globina: int = 0) -> str:
        return (
            globina * "  " + "<=\n" +
            self.l.drevo(globina + 1) + 
            self.r.drevo(globina + 1)
        )

    def optimiziran(self, nivo: int = 0) -> TVozlišče:
        return VečjeEnako(self.r, self.l).optimiziran(nivo)

    def prevedi(self) -> str:
        return self.optimiziran().prevedi()

class Če(Vozlišče):
    pogoj: Vozlišče
    resnica: Vozlišče
    laž: Vozlišče

    def __init__(self, pogoj: Vozlišče, resnica: Vozlišče, laž: Vozlišče):
        self.pogoj = pogoj
        self.resnica = resnica
        self.laž = laž
        if len(self.resnica) != len(self.laž):
            return Exception("resnica and laž morata imeti enako velik stack")

    def __len__(self) -> int:
        return len(self.resnica)

    def drevo(self, globina: int = 0) -> str:
        return (
            "if (\n" +
            self.pogoj.drevo(globina +  1) +
            ") {\n" +
            self.resnica.drevo(globina + 1) +
            "}\nelse {\n" +
            self.laž.drevo(globina + 1)
        )

    def optimiziran(self, nivo: int = 0) -> Vozlišče:
        opti = Če(
            self.pogoj.optimiziran(nivo),
            self.resnica.optimiziran(nivo),
            self.laž.optimiziran(nivo)
        )

        if nivo == 0: return opti

        if opti.pogoj == Resnica():
            return opti.resnica
        elif opti.pogoj == Laž():
            return opti.laž

        if nivo == 1: return opti

        return opti

    def prevedi(self) -> str:
        resnica_ukazi = self.resnica.prevedi()
        resnica_len = len(resnica_ukazi.split('\n'))
        laž_ukazi = self.laž.prevedi()
        laž_len = len(laž_ukazi.split('\n'))

        return (
            self.pogoj.prevedi() +
            f"IF +{laž_len + 1}\n" +
            laž_ukazi +
            f"JMP +{resnica_len}\n" +
            resnica_ukazi
        )

class Prirejanje(Vozlišče):
    spremenljivka: Spremenljivka
    izraz: Izraz
    nova_spr: bool

    def __init__(self, spremenljivka: Spremenljivka, izraz: Izraz, nova_spr: bool):
        self.spremenljivka = spremenljivka
        self.izraz = izraz
        self.nova_spr = nova_spr

    def __len__(self) -> int:
        return 1 if self.nova_spr else 0

    def __eq__(self, o: object) -> bool:
        return (
            self.spremenljivka == o.spremenljivka
            and self.izraz == o.izraz
            and self.nova_spr == o.nova_spr
        )

    def drevo(self, globina: int = 0) -> str:
        return (
            globina * "  " + str(self.spremenljivka) + " =\n" +
            self.izraz.drevo(globina + 1)
        )

    def optimiziran(self, nivo: int = 0) -> TIzraz:
        opti = Prirejanje(self.spremenljivka, self.izraz.optimiziran(nivo), self.nova_spr)
        return opti

    def prevedi(self) -> str:
        return self.izraz.prevedi() + (
            (
                f"MOV @{self.spremenljivka.naslov}\n" +
                "POP\n"
            ) if not self.nova_spr 
            else ""
        )

class Zaporedje(Izraz):
    def __len__(self) -> int:
        return len(self.l) + len(self.r)

    def drevo(self, globina: int = 0, reverse = False) -> str:
        return (
            self.r.drevo(globina) +
            globina * "  " + ",\n" + (
                self.l.drevo(globina, reverse)
                    if type(self.l) is Zaporedje 
                    else self.l.drevo(globina)
            )

        ) if reverse else (
            self.l.drevo(globina) +
            globina * "  " + ",\n" +
            self.r.drevo(globina)
        )

    def optimiziran(self, nivo: int = 0) -> TIzraz:
        opti = Zaporedje(self.l.optimiziran(nivo), self.r.optimiziran(nivo))
        return opti

    def prevedi(self) -> str:
        return (
            self.l.prevedi() +
            self.r.prevedi()
        )

class Natisni(Vozlišče):
    izrazi: Zaporedje

    def __init__(self, izrazi: Zaporedje):
        self.izrazi = izrazi

    def __len__(self) -> int:
        return 0

    def __eq__(self, o: object) -> bool:
        return type(o) is Natisni and self.izrazi == o.izrazi

    def drevo(self, globina: int = 0) -> str:
        return (
            globina * "  " + "natisni(\n" + (
                self.izrazi.drevo(globina + 1, True)
                    if type(self.izrazi) is Zaporedje 
                    else self.izrazi.drevo(globina + 1)
            ) +
            globina * "  " + ")\n"
        )

    def optimiziran(self, nivo: int = 0) -> TVozlišče:
        return Natisni(self.izrazi.optimiziran(nivo))

    def prevedi(self) -> str:
        return (
            self.izrazi.prevedi() +
            "PRINT\n" * len(self.izrazi)
        )

TOkvir = TypeVar("TOkvir", bound="Okvir")

class Okvir(Vozlišče):
    zaporedje: Zaporedje

    def __init__(self, zaporedje: Zaporedje):
        self.zaporedje = zaporedje

    def __len__(self) -> int:
        return len(self.zaporedje)

    def __eq__(self, o: object) -> bool:
        return type(o) is Okvir and self.zaporedje == o.zaporedje

    def drevo(self, globina: int = 0) -> str:
        return (
            globina * "  " + "{\n" +
            self.zaporedje.drevo(globina + 1) +
            globina * "  " + "}\n"
        )

    def optimiziran(self, nivo: int = 0) -> TOkvir:
        return Okvir(self.zaporedje.optimiziran(nivo))

    def prevedi(self) -> str:
        return (
            self.zaporedje.prevedi() +
            "POP\n" * len(self.zaporedje)
        )

class FunkcijskiKlic(Vozlišče):
    ime: str
    argumenti: Zaporedje
    okvir: Okvir

    def __init__(self, ime: str, argumenti: Zaporedje, ukazi: Vozlišče):
        self.ime = ime
        self.argumenti = argumenti
        self.okvir = ukazi

    def drevo(self, globina: int = 0) -> str:
        return (
            globina * "  " + "{\n" +
            self.zaporedje.drevo(globina+1) +
            globina * "  " + "}\n"
        )

    def optimiziran(self, nivo: int = 0) -> TVozlišče:
        return FunkcijskiKlic(
            self.ime, 
            [ arg.optimiziran(nivo) for arg in self.argumenti ], 
            self.okvir.optimiziran(nivo)
        )

    def prevedi(self) -> str:
        return (
            self.argumenti.prevedi() +
            self.ukaz + '\n' +
            "POP\n" * len(self.argumenti)
        )
