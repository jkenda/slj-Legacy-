#!/usr/bin/python3

from operator import add, sub, mul, truediv, mod
import sys

ukazi = { "ADD": add, "SUB": sub, "MUL": mul, "DIV": truediv, "MOD": mod, "POW": pow }

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
            if not lines[pc] or lines[pc].isspace():
                # prazna vrstica
                pc += 1
                continue

            besede = lines[pc].split(' ')
            ukaz = besede[0]
            if ukaz.startswith('#'):
                # komentar
                pc +=1
                continue

            if ukaz == "JMP":
                tip = besede[1][0]
                stevilka = int(besede[1][1:])
                if tip == '#':
                    pc = stevilka - 1
                elif tip == '@':
                    pc = stack[stevilka] - 1
            if ukaz == "PUSH":
                tip = besede[1][0]
                stevilka = besede[1][1:]
                if tip == '@':
                    # naslov
                    stack.append(stack[int(stevilka)])
                elif tip == '#':
                    # literal
                    stack.append((float(stevilka)))
                else:
                    # string
                    stack.append(besede[1][1:-1])
            elif ukaz == "POP":
                stack.pop()
            elif ukaz == "MOV":
                stevilka = int(besede[1][1:])
                stack[stevilka] = stack[-1]
            elif ukaz == "PRINT":
                if not print_stack: print(str(stack[-1]))
            else:
                stack[-2] = ukazi[ukaz](stack[-2], stack[-1])
                stack.pop()

            if print_stack: print(lines[pc] + ":", stack)

            pc += 1
            if len(stack) == 0:
                break

if __name__ == "__main__":
    exit(main(len(sys.argv), sys.argv))
