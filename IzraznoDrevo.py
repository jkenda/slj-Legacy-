from typing import TypeVar
from collections.abc import Callable
from operator import add, sub, mul, truediv

TIzraznoDrevo = TypeVar("TIzraznoDrevo", bound="IzraznoDrevo")

operatorji_r = { add: '+', sub: '-', mul: '*', truediv: '/', pow: '^' }
ukazi_r = { add: "ADD", sub: "SUB", mul: "MUL", truediv: "DIV", pow: "POW" }
ukazi = { ukaz: op for op, ukaz in ukazi_r.items() }

class IzraznoDrevo:
    data: Callable[[float, float], float] | float | str
    l: TIzraznoDrevo | None
    r: TIzraznoDrevo | None

    def __init__(self, data, l = None, r = None) -> None:
        self.data = data
        self.l = l
        self.r = r

    def print(self, spremenljivke: dict, globina: int = 0):
        print(globina * "  ", end="")

        if type(self.data) is float:
            print(str(self.data))
        elif type(self.data) is str:
            print(f"{self.data} ({spremenljivke[self.data]})")
        else:
            print(operatorji_r[self.data])
            self.l.print(spremenljivke, globina + 1)
            self.r.print(spremenljivke, globina + 1)

    def ovrednoti(self, spremenljivke: dict) -> float:
        if type(self.data) == float:
            return self.data
        if type(self.data) is str:
            return spremenljivke[self.data]
        else:
            return self.data(
                self.l.ovrednoti(spremenljivke), 
                self.r.ovrednoti(spremenljivke)
            )

    def compile(self, spremenljivke: dict):
        if type(self.data) == float:
            return f"PUSH {self.data}"
        if type(self.data) is str:
            return f"PUSH {spremenljivke[self.data]}"
        else:
            return (
                f"{self.l.compile(spremenljivke)}\n"
                f"{self.r.compile(spremenljivke)}\n"
                f"{ukazi_r[self.data]}"
            )

    def zaženi(program: str) -> float:
        stack = []

        lines = program.split('\n')

        for line in lines:
            besede = line.split(' ')
            ukaz = besede[0]

            if ukaz == "PUSH":
                stack.append(float(besede[1]))
            elif ukaz == "POP":
                stack.pop()
            else:
                stack[-2] = ukazi[ukaz](stack[-2], stack[-1])
                stack.pop()

            print(line + ":", stack)

        print("=", stack[-1])
