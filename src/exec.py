#!/usr/bin/python3

from enum import Enum, auto, unique
from operator import add, sub, mul, truediv, mod
import sys

@unique
class Ukaz(Enum):
    JUMP  = auto()
    JMPC  = auto()
    PUSH  = auto()
    POP   = auto()
    POS   = auto()
    ZERO  = auto()
    LOAD  = auto()
    STORE = auto()
    PRINT = auto()

class UkazPodatek:
    ukaz: Ukaz
    podatek: float | int | str | None

    def __init__(self, ukaz: Ukaz, podatek: float | int | str = None) -> None:
        self.ukaz = ukaz
        self.podatek = podatek

UKAZI = { "ADD": add, "SUB": sub, "MUL": mul, "DIV": truediv, "MOD": mod, "POW": pow }
RESNICA = 1.0; LAŽ = 0.0


def run(program: list[UkazPodatek], print_stack: bool):
    stack = []
    pc = 0

    while pc < len(program):
        ukaz = program[pc]

        if print_stack: print(str(program[pc].ukaz) + ": ", end="")

        if ukaz.ukaz is Ukaz.JUMP:
            pc = ukaz.podatek
        elif ukaz.ukaz is Ukaz.JMPC:
            if stack[-1] == RESNICA:
                pc = ukaz.podatek
            stack.pop()
        elif ukaz.ukaz is Ukaz.PUSH:
            stack.append(ukaz.podatek)
        elif ukaz.ukaz is Ukaz.POP:
            stack.pop()
        elif ukaz.ukaz is Ukaz.POS:
            stack[-1] = RESNICA if stack[-1] > 0 else LAŽ
        elif ukaz.ukaz is Ukaz.ZERO:
            stack[-1] = RESNICA if stack[-1] == 0 else LAŽ
        elif ukaz.ukaz is Ukaz.LOAD:
            stack.append(stack[ukaz.podatek])
        elif ukaz.ukaz is Ukaz.STORE:
            stack[ukaz.podatek] = stack[-1]
            stack.pop()
        elif ukaz.ukaz is Ukaz.PRINT:
            if not print_stack: 
                print(str(stack[-1]), end="")
            stack.pop()
        else:
            stack[-2] = ukaz.ukaz(stack[-2], stack[-1])
            stack.pop()

        if print_stack: print(stack)
        pc += 1

def main(argc: int, argv: list[str]) -> int:
    if argc not in [2, 3]:
        return 1

    program: list[UkazPodatek] = []

    print_stack = False
    if "-s" in argv[1:-1]:
        print_stack = True

    with open(argv[-1], "r") as file:
        vrstice = list(map(lambda l: l.strip(), file.readlines()))

        for vrstica in vrstice:
            if not vrstica or vrstica.isspace():
                # prazna vrstica
                continue
            
            ukaz = vrstica.strip().split(' ')[0]

            if ukaz.startswith('#'):
                # komentar
                continue
            elif ukaz == "JUMP":
                # samo absolutni skoki
                ostanek = vrstica[len(ukaz)+1:]
                program.append(UkazPodatek(Ukaz.JUMP, int(ostanek[1:]) - 1))
            elif ukaz == "JMPC":
                # samo absolutni skoki
                ostanek = vrstica[len(ukaz)+1:]
                program.append(UkazPodatek(Ukaz.JMPC, int(ostanek[1:]) - 1))
            elif ukaz == "POS":
                program.append(UkazPodatek(Ukaz.POS))
            elif ukaz == "ZERO":
                program.append(UkazPodatek(Ukaz.ZERO))
            elif ukaz == "PUSH":
                ostanek = vrstica[len(ukaz)+1:]
                tip = ostanek[0]
                if tip == '#':
                    # literal
                    program.append(UkazPodatek(Ukaz.PUSH, float(ostanek[1:])))
                elif tip == '"':
                    # 4 chars
                    string = ostanek[1:-1]
                    string = string.replace('\\n', '\n')
                    string = string.replace('\\r', '\r')
                    string = string.replace('\\t', '\t')
                    program.append(UkazPodatek(Ukaz.PUSH, string))
            elif ukaz == "LOAD":
                ostanek = vrstica[len(ukaz)+1:]
                # naslov
                program.append(UkazPodatek(Ukaz.LOAD, int(ostanek[1:])))
            elif ukaz == "POP":
                program.append(UkazPodatek(Ukaz.POP))
            elif ukaz == "STORE":
                ostanek = vrstica[len(ukaz)+1:]
                program.append(UkazPodatek(Ukaz.STORE, int(ostanek[1:])))
            elif ukaz in ["PRINTN", "PRINTS"]:
                ostanek = vrstica[len(ukaz)+1:]
                program.append(UkazPodatek(Ukaz.PRINT))
            else:
                program.append(UkazPodatek(UKAZI[ukaz]))

    run(program, print_stack)


if __name__ == "__main__":
    exit(main(len(sys.argv), sys.argv))
