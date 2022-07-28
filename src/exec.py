#!/usr/bin/python3

from operator import add, sub, mul, truediv, mod
import sys

UKAZI = { "ADD": add, "SUB": sub, "MUL": mul, "DIV": truediv, "MOD": mod, "POW": pow }
RESNICA = 1.0; LAŽ = 0.0

def main(argc: int, argv: list[str]) -> int:
    if argc not in [2, 3]:
        return 1

    print_stack = False
    if "-s" in argv[1:-1]:
        print_stack = True

    with open(argv[-1], "r") as file:
        lines = list(map(lambda l: l.strip(), file.readlines()))

        stack = []
        pc = 0

        while True:
            if pc >= len(lines):
                break
            if not lines[pc] or lines[pc].isspace():
                # prazna vrstica
                pc += 1
                continue
            
            if print_stack: print(lines[pc] + ": ", end="")

            ukaz = lines[pc].strip().split(' ')[0]

            if ukaz.startswith('#'):
                # komentar
                pc +=1
                continue
            elif ukaz == "JUMP":
                # samo absolutni skoki
                ostanek = lines[pc][len(ukaz)+1:]
                tip = ostanek[0]
                pc = int(ostanek[1:]) - 1
            elif ukaz == "JMPC":
                # samo absolutni skoki
                ostanek = lines[pc][len(ukaz)+1:]
                tip = ostanek[0]
                if stack[-1] == RESNICA:
                    pc = int(ostanek[1:]) - 1
                stack.pop()
            elif ukaz == "POS":
                stack[-1] = RESNICA if stack[-1] > 0 else LAŽ
            elif ukaz == "ZERO":
                stack[-1] = RESNICA if stack[-1] == 0 else LAŽ
            
            elif ukaz == "PUSH":
                ostanek = lines[pc][len(ukaz)+1:]
                tip = ostanek[0]
                if tip == '#':
                    # literal
                    stack.append((float(ostanek[1:])))
                elif tip == '"':
                    # char
                    char = ostanek[1:-1]
                    char = char.replace('\\n', '\n')
                    char = char.replace('\\r', '\r')
                    char = char.replace('\\t', '\t')
                    stack.append(char)
            elif ukaz == "LOAD":
                ostanek = lines[pc][len(ukaz)+1:]
                # naslov
                stack.append(stack[int(ostanek[1:])])
            elif ukaz == "POP":
                stack.pop()
            elif ukaz == "STORE":
                ostanek = lines[pc][len(ukaz)+1:]
                stack[int(ostanek[1:])] = stack[-1]
                stack.pop()
            elif ukaz == "PRINT":
                ostanek = lines[pc][len(ukaz)+1:]
                if not print_stack: print(str(stack[-1]), end="")
                stack.pop()
            else:
                stack[-2] = UKAZI[ukaz](stack[-2], stack[-1])
                stack.pop()

            if print_stack: print(stack)

            pc += 1

if __name__ == "__main__":
    exit(main(len(sys.argv), sys.argv))
