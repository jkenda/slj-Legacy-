#!/usr/bin/python3

from ..src.IzraznoDrevo import *

def prazno():
    p1 = Prazno()
    p2 = Prazno()
    assert(p1 == p2)
    assert(p1.drevo(2) == "    ()\n")
    assert(p1.optimiziran() == Prazno())
    assert(p1.prevedi() == "")
    print("OK")

def niz():
    n1 = Niz("aa")
    n2 = Niz("aa")
    n3 = Niz("ab\n")
    assert(n1 == n2)
    assert(n1 != n3)
    assert(n2 != n3)
    assert(len(n1) == 1)
    assert(n1 + n2 + n3 == Niz("aaaaab\n"))
    assert(len(n1 + n2 + n3) == 2)
    assert(n3 * 2 == Niz("ab\nab\n"))
    assert(n1.drevo(2) == '    "aa"\n')
    assert(n1.optimiziran(2) == n1)
    assert((n1 + n2 + n3).prevedi() == 'PUSH "ab\\n"\nPUSH "aaaa"\n')
    print("OK")

def število():
    š1 = Število(1.0)
    š2 = Število(1.0)
    š3 = Število(2.0)
    assert(š1 == š2)
    assert(š1 != š3)
    assert(š2 != š3)
    assert(len(š1) == 1)
    assert(float(š1) == float(š2))
    assert(int(š1) == int(š2))
    assert(š1 + š2 + š3 == Število(4.0))
    assert(š3 - š2 - š1 == Število(0.0))
    assert(š2 * š3 == Število(2.0))
    assert(š2 / š3 == Število(0.5))
    assert(š2 ** š3 == Število(1.0))
    assert(š3 % š2 == Število(0.0))
    assert(š1.drevo(2) == '    1.0\n')
    assert(š2.optimiziran(2) == š2)
    assert(š1.prevedi() == 'PUSH #1.0\n')
    print("OK")

def spremenljivka():
    s1 = Spremenljivka("x", 0)
    s2 = Spremenljivka("x", 0)
    s3 = Spremenljivka("y", 1)
    assert(len(s1) == 1)
    assert(str(s2) == "x @0")
    assert(s1 == s2)
    assert(s1 != s3)
    assert(s2 != s3)
    assert(s3.drevo(2) == "    y @1\n")
    assert(s2.optimiziran(2) == s2)
    assert(s1.prevedi() == "LOAD @0\n")
    print("OK")

def seštevanje():
    p1 = Seštevanje(Število(1), Število(-1))
    p2 = Seštevanje(Število(1), Število(-1))
    p3 = Seštevanje(Število(-1), Število(1))
    assert(p1 == p2)
    assert(p1 != p3)
    assert(p2 != p3)
    assert(p1.drevo(1) == f"  +\n{Število(1).drevo(2)}{Število(-1).drevo(2)}")
    assert(p2.optimiziran(1) == p3.optimiziran(1))
    assert(p3.prevedi() == f"{Število(-1).prevedi()}{Število(1).prevedi()}ADD\n")
    print("OK")

def odštevanje():
    m1 = Odštevanje(Število(1), Število(-1))
    m2 = Odštevanje(Število(1), Število(-1))
    m3 = Odštevanje(Število(0), Število(-2))
    assert(m1 == m2)
    assert(m1 != m3)
    assert(m2 != m3)
    assert(m1.drevo(1) == f"  -\n{Število(1).drevo(2)}{Število(-1).drevo(2)}")
    assert(m2.optimiziran(1) == m3.optimiziran(1))
    assert(m3.prevedi() == f"{Število(0).prevedi()}{Število(-2).prevedi()}SUB\n")
    print("OK")

def množenje():
    k1 = Množenje(Število(2), Število(3))
    k2 = Množenje(Število(2), Število(3))
    k3 = Množenje(Število(1), Število(6))
    assert(k1 == k2)
    assert(k1 != k3)
    assert(k2 != k3)
    assert(k1.drevo(1) == f"  *\n{Število(2).drevo(2)}{Število(3).drevo(2)}")
    assert(k2.optimiziran(1) == k3.optimiziran(1))
    assert(k3.prevedi() == f"{Število(1).prevedi()}{Število(6).prevedi()}MUL\n")
    print("OK")

def deljenje():
    d1 = Deljenje(Število(10), Število(5))
    d2 = Deljenje(Število(10), Število(5))
    d3 = Deljenje(Število(4), Število(2))
    assert(d1 == d2)
    assert(d1 != d3)
    assert(d2 != d3)
    assert(d1.drevo(1) == f"  /\n{Število(10).drevo(2)}{Število(5).drevo(2)}")
    assert(d2.optimiziran(1) == d3.optimiziran(1))
    assert(d3.prevedi() == f"{Število(4).prevedi()}{Število(2).prevedi()}DIV\n")
    print("OK")

def modulo():
    d1 = Modulo(Število(7), Število(4))
    d2 = Modulo(Število(7), Število(4))
    d3 = Modulo(Število(8), Število(5))
    assert(d1 == d2)
    assert(d1 != d3)
    assert(d2 != d3)
    assert(d1.drevo(1) == f"  %\n{Število(7).drevo(2)}{Število(4).drevo(2)}")
    assert(d2.optimiziran(1) == d3.optimiziran(1))
    assert(d3.prevedi() == f"{Število(8).prevedi()}{Število(5).prevedi()}MOD\n")
    print("OK")

def potenca():
    d1 = Potenca(Število(2), Število(4))
    d2 = Potenca(Število(2), Število(4))
    d3 = Potenca(Število(4), Število(2))
    assert(d1 == d2)
    assert(d1 != d3)
    assert(d2 != d3)
    assert(d1.drevo(1) == f"  ^\n{Število(2).drevo(2)}{Število(4).drevo(2)}")
    assert(d2.optimiziran(1) == d3.optimiziran(1))
    assert(d3.prevedi() == f"{Število(4).prevedi()}{Število(2).prevedi()}POW\n")
    print("OK")

def prirejanje():
    p1 = Prirejanje(Spremenljivka("x", 0), Število(3), True)
    p2 = Prirejanje(Spremenljivka("x", 0), Število(3), True)
    p3 = Prirejanje(Spremenljivka("x", 0), Seštevanje(Število(2), Število(1)), True)
    p4 = Prirejanje(Spremenljivka("x", 0), Število(3), False)
    assert(len(p1) == 1)
    assert(len(p4) == 0)
    assert(p1 == p2)
    assert(p2 != p3)
    assert(p1 != p4)
    assert(p2 != p4)
    assert(p2.drevo(1) == f"  x @0 =\n{Število(3).drevo(2)}")
    assert(p2.optimiziran(1) == p3.optimiziran(1))
    assert(p2.prevedi() == Število(3).prevedi())
    assert(p4.prevedi() == Število(3).prevedi() + "STOR @0\nPOP\n")
    print("OK")

def zaporedje():
    p1 = Prirejanje(Spremenljivka("x", 0), Število(3), True)
    p2 = Prirejanje(Spremenljivka("y", 1), Število(4), True)
    p3 = Prirejanje(Spremenljivka("x", 0), Število(5), False)
    n = Natisni(Število(1))
    z1 = Zaporedje(
        Zaporedje(
            Zaporedje(
                p1,
                p2,
            ),
            p3
        ),
        n
    )
    assert(len(z1) == 2)
    assert(z1.optimiziran(2) == z1)
    assert(z1.prevedi() == p1.prevedi() + p2.prevedi() + p3.prevedi() + n.prevedi())
    print("OK")

def natisni():
    n1 = Natisni(Zaporedje(
        Število(2),
        Število(1)
    ))
    n2 = Natisni(Zaporedje(
        Število(2),
        Število(1)
    ))

    izrazi = Zaporedje(
        Odštevanje(Število(3), Število(1)),
        Število(1)
    )
    n3 = Natisni(izrazi)
    assert(len(n1) == 0)
    assert(n1 == n2)
    assert(n1 != n3)
    assert(n2 != n3)
    assert(n1.optimiziran(1) == n3.optimiziran(1))
    assert(n3.prevedi() == izrazi.prevedi() + "PRINT\n" * len(izrazi))
    print("OK")

def okvir():
    z1 = Zaporedje(
        Prirejanje(Spremenljivka("x", 0), Seštevanje(Število(0), Število(1)), True),
        Prirejanje(Spremenljivka("x", 0), Seštevanje(Spremenljivka("x", 0), Število(1)), False)
    )
    z2 = Zaporedje(
        Prirejanje(Spremenljivka("x", 0), Število(1), True),
        Prirejanje(Spremenljivka("x", 0), Seštevanje(Spremenljivka("x", 0), Število(1)), False)
    )
    o1 = Okvir(z1)
    o2 = Okvir(z2)
    assert(len(o1) == len(z1))
    assert(o1 != o2)
    assert(o1.drevo(1) == "  {\n" + z1.drevo(2) + "  }\n")
    assert(o1.optimiziran(1) == o2.optimiziran(1))
    assert(o2.prevedi() == z2.prevedi() + "POP\n" * len(z2))
    print("OK")

def funkcijski_klic():
    assert(False)
    print("OK")

testi = [
    prazno,
    niz,
    število,
    spremenljivka,
    seštevanje,
    odštevanje,
    množenje,
    deljenje,
    modulo,
    potenca,
    prirejanje,
    natisni,
    zaporedje,
    okvir,
    #funkcijski_klic,
]

for test in testi:
    print(test.__name__ + ": ")
    test()
    print()
print("Vse OK.")
