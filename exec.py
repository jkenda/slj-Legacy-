#!/usr/bin/python3

from operator import add, sub, mul, truediv
import sys

ukazi = { "ADD": add, "SUB": sub, "MUL": mul, "DIV": truediv, "POW": pow }

def main(argc: int, argv: list[str]) -> int:
    if argc != 2:
        return 1

    with open(argv[1], "r") as file:
        lines = map(lambda l: l.strip(), file.readlines())

        stack = []

        for line in lines:
            if not line or line.isspace():
                i += 1
                continue

            # print(line + ":", end=" ")
            besede = line.split(' ')
            ukaz = besede[0]

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
                print(str(stack[-1]))
            else:
                stack[-2] = ukazi[ukaz](stack[-2], stack[-1])
                stack.pop()

            # print(stack)

if __name__ == "__main__":
    exit(main(len(sys.argv), sys.argv))
