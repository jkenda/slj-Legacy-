#!/usr/bin/python3

from typing import TypeVar
from collections.abc import Callable
from operator import add, sub, mul, truediv

operatorji_r = { add: '+', sub: '-', mul: '*', truediv: '/', pow: '^' }

TTree = TypeVar("TTree", bound="Tree")

class Tree:
	data: Callable[[float, float], float] | float
	l: TTree | None
	r: TTree | None

	def __init__(self, data, l = None, r = None) -> None:
		self.data = data
		self.l = l
		self.r = r

	def print(self, globina: int = 0):
		print(globina * "  ", end="")

		if type(self.data) is float:
			print(str(self.data))
		elif type(self.data) is str:
			print(f"{self.data} ({consts[self.data]})")
		else:
			print(operatorji_r[self.data])
			self.l.print(globina + 1)
			self.r.print(globina + 1)

	def ovrednoti(self) -> float:
		if type(self.data) == float:
			return self.data
		if type(self.data) is str:
			return consts[self.data]
		else:
			return self.data(self.l.ovrednoti(), self.r.ovrednoti())

operatorji = { '+': add, '-': sub, '*': mul, '/': truediv, '^': pow }
ignore = { '+', '-', '*', '/', '^', ')' }

consts = {
	"e":   2.7182818284590452354,
	"phi": 1.61803398874989485,
	"pi":  3.14159265358979323846,
}

def main():
	izraz = "\0"
	while izraz != "":
		try:
			izraz = input("> ")
			tree = izgradi(izraz)
			tree.print()
			print("\n=", tree.ovrednoti())
		except (KeyboardInterrupt, EOFError):
			print()
			exit()
		except Exception as e:
			print(e)


def izgradi(izraz: str) -> Tree:
	predprocesiran_izraz = predprocesiran(izraz)
	print(predprocesiran_izraz)
	return aditivni(predprocesiran_izraz)

def predprocesiran(izraz: str) -> str:
	# odstrani presledke
	predproc_str = izraz.replace(" ", "")

	# dodaj znak '*' v implicitno množenje
	i = 1
	dolzina = len(predproc_str)
	while i < dolzina:
		prev = predproc_str[i-1]; curr = predproc_str[i]
		if prev.isnumeric() and not curr.isnumeric() and not curr in ignore:
			predproc_str = predproc_str[:i] + '*' + predproc_str[i:]
		elif curr == '(' and prev.isalnum():
			predproc_str = predproc_str[:i] + '*' + predproc_str[i:]
		elif prev == ')':
			if not curr.isnumeric() and not curr in ignore:
				predproc_str = predproc_str[:i] + '*' + predproc_str[i:]
			if curr.isnumeric():
				predproc_str = predproc_str[:i] + '*' + predproc_str[i:]
		i += 1

	return predproc_str

def aditivni(izraz: str) -> Tree:
	plus  = poišči(izraz, '+')
	minus = poišči(izraz, '-')

	if plus == -1 and minus == -1:
		# ni ne '+', ne '-'
		return multiplikativni(izraz)
	elif plus > minus:
		# '+' ima prednost
		return Tree(add, aditivni(izraz[:plus]), multiplikativni(izraz[plus+1:]))
	elif minus > plus:
		# '-' ima prednost 
		if minus == 0:
			# negacija na začetku izraza
			return multiplikativni(izraz)
		elif izraz[minus-1] in operatorji:
			# negacija
			return Tree(operatorji[izraz[minus-1]], aditivni(izraz[:minus-1]), multiplikativni(izraz[minus:]))
		else:
			# odštevanje
			return Tree(sub, aditivni(izraz[:minus]), multiplikativni(izraz[minus+1:]))

def multiplikativni(izraz: str) -> float:
	krat    = poišči(izraz, '*')
	deljeno = poišči(izraz, '/')

	if krat == -1 and deljeno == -1:
		# ni ne '+', ne'/'
		return potenčni(izraz)
	elif krat > deljeno:
		# '*' ima prednost
		return Tree(mul, multiplikativni(izraz[:krat]), potenčni(izraz[krat+1:]))
	elif deljeno > krat:
		# '/' ima prednost
		return Tree(truediv, multiplikativni(izraz[:deljeno]), potenčni(izraz[deljeno+1:]))

def potenčni(izraz: str) -> Tree:
	na = poišči(izraz, '^')

	if na == -1:
		# ni znaka '^'
		return osnovni(izraz)
	return Tree(pow, potenčni(izraz[:na]), potenčni(izraz[na+1:]))

def osnovni(izraz: str) -> float:
	if len(izraz) == 0:
		return Tree(0.0)
	if izraz[0] == '(':
		return aditivni(izraz[1:-1])

	try:
		return Tree(float(izraz))
	except Exception:
		if izraz in consts:
			return Tree(izraz)
		else:
			raise Exception(f"'{izraz}' not defined.")

def poišči(izraz: str, niz: str) -> int:
	oklepajev = 0

	i = len(izraz) - 1
	while i >= 0:
		if izraz[i] == ')':
			oklepajev += 1
		elif izraz[i] == '(':
			oklepajev -= 1

		if oklepajev == 0 and izraz[i:].startswith(niz):
			# iskani znak ni znotraj oklepajev
			return i
		i -= 1

	if oklepajev != 0:
		raise Exception("Oklepaji se ne ujemajo.")

	return -1

if __name__ == "__main__":
	main()
