from abc import abstractmethod
from typing import TypeVar, overload
from collections.abc import Callable
from operator import add, sub, mul, truediv

TNode = TypeVar("TNode", bound="Node")

operatorji_r = { add: '+', sub: '-', mul: '*', truediv: '/', pow: '^' }
ukazi_r = { add: "ADD", sub: "SUB", mul: "MUL", truediv: "DIV", pow: "POW" }
ukazi = { ukaz: op for op, ukaz in ukazi_r.items() }

class Node:
    l: TNode
    r: TNode

    def __init__(self, l: TNode, r: TNode) -> None:
        self.l = l
        self.r = r

    @abstractmethod
    def print(self, spremenljivke: dict, globina: int = 0):
        pass

    @abstractmethod
    def ovrednoti(self, spremenljivke: dict) -> float:
        pass

    @abstractmethod
    def compile(self, spremenljivke: dict) -> str:
        pass

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

class Num(Node):
    data: float

    def __init__(self, data: float) -> None:
        self.data = data

    def print(self, _: dict, globina: int = 0):
        print(globina * "  " + str(self.data))

    def ovrednoti(self, _: dict):
        return self.data

    def compile(self, _: dict):
        return f"PUSH {self.data}"

class Var(Node):
    data: str

    def print(self, spremenljivke: dict, globina: int = 0):
        print(globina * "  " + f"{self.data} ({spremenljivke[self.data]})")

    def ovrednoti(self, spremenljivke: dict) -> float:
        return spremenljivke[self.data]

    def compile(self, spremenljivke: dict) -> str:
        return f"PUSH {spremenljivke[self.data]}"

class Pow(Node):
    def print(self, spremenljivke: dict, globina: int = 0):
        print(globina * "  " + '^')
        self.l.print(spremenljivke, globina + 1)
        self.r.print(spremenljivke, globina + 1)

    def ovrednoti(self, spremenljivke: dict) -> float:
        return self.l.ovrednoti(spremenljivke) ** self.r.ovrednoti(spremenljivke)

    def compile(self, spremenljivke: dict) -> str:
        return (
            f"{self.l.compile(spremenljivke)}\n"
            f"{self.r.compile(spremenljivke)}\n"
            f"POW"
        )

class Mul(Node):
    def print(self, spremenljivke: dict, globina: int = 0):
        print(globina * "  " + '*')
        self.l.print(spremenljivke, globina + 1)
        self.r.print(spremenljivke, globina + 1)

    def ovrednoti(self, spremenljivke: dict) -> float:
        return self.l.ovrednoti(spremenljivke) * self.r.ovrednoti(spremenljivke)

    def compile(self, spremenljivke: dict) -> str:
        return (
            f"{self.l.compile(spremenljivke)}\n"
            f"{self.r.compile(spremenljivke)}\n"
            f"MUL"
        )

class Div(Node):
    def print(self, spremenljivke: dict, globina: int = 0):
        print(globina * "  " + '/')
        self.l.print(spremenljivke, globina + 1)
        self.r.print(spremenljivke, globina + 1)

    def ovrednoti(self, spremenljivke: dict) -> float:
        return self.l.ovrednoti(spremenljivke) / self.r.ovrednoti(spremenljivke)

    def compile(self, spremenljivke: dict) -> str:
        return (
            f"{self.l.compile(spremenljivke)}\n"
            f"{self.r.compile(spremenljivke)}\n"
            f"DIV"
        )

class Add(Node):
    def print(self, spremenljivke: dict, globina: int = 0):
        print(globina * "  " + '+')
        self.l.print(spremenljivke, globina + 1)
        self.r.print(spremenljivke, globina + 1)

    def ovrednoti(self, spremenljivke: dict) -> float:
        return self.l.ovrednoti(spremenljivke) + self.r.ovrednoti(spremenljivke)

    def compile(self, spremenljivke: dict) -> str:
        return (
            f"{self.l.compile(spremenljivke)}\n"
            f"{self.r.compile(spremenljivke)}\n"
            f"ADD"
        )

class Sub(Node):
    def print(self, spremenljivke: dict, globina: int = 0):
        print(globina * "  " + '+')
        self.l.print(spremenljivke, globina + 1)
        self.r.print(spremenljivke, globina + 1)

    def ovrednoti(self, spremenljivke: dict) -> float:
        return self.l.ovrednoti(spremenljivke) - self.r.ovrednoti(spremenljivke)

    def compile(self, spremenljivke: dict) -> str:
        return (
            f"{self.l.compile(spremenljivke)}\n"
            f"{self.r.compile(spremenljivke)}\n"
            f"SUB"
        )
