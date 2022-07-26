#!/usr/bin/python3

from curses.ascii import isalpha
from operator import add, sub, mul, truediv
import re
from IzraznoDrevo import *

operatorji = { '+': Seštevanje, '-': Odštevanje, '*': Množenje, '/': Deljenje, '^': Potenca }
ignore = { '+', '-', '*', '/', '^', ')' }
var_regex = r"[a-zA-Z_]\w*"

konstante = {
	"e":   2.7182818284590452354,
	"pi":  3.14159265358979323846,
	"phi": 1.61803398874989485,
	"psi": 1.46557123187676802665,
	"mu":  1.84775906502257351225,
	"K":   0.11494204485329620070,
}

spremenljivke = dict()


def main():
	izraz = "\0"
	while izraz != "":
		try:
			vrednost = priredi(input("> "))
			print("\n=", vrednost)
		except (KeyboardInterrupt, EOFError):
			print()
			exit()
		except Exception as e:
			print(e)


def priredi(izraz: str) -> float:
	st_enacajev = izraz.count('=')
	spremenljivka = None

	if st_enacajev > 1:
		raise Exception("Preveč enačajev.")
	elif st_enacajev == 1:
		razdeljen = list(map(lambda x: x.strip(), izraz.split('=')))
		if re.fullmatch(var_regex, razdeljen[0]):
			if razdeljen[0] not in konstante:
				spremenljivka = razdeljen[0]
				izraz = razdeljen[1]
			else:
				raise Exception(f"'{razdeljen[0]}' je konstanta.")
		else:
			raise Exception(f"Neveljavno ime: '{razdeljen[0]}'")

	tree = izgradi(izraz)
	tree.print(konstante | spremenljivke)
	program = tree.compile(konstante | spremenljivke)
	print(program)
	IzraznoDrevo.zaženi(program)
	vrednost = tree.ovrednoti(konstante | spremenljivke)
	if spremenljivka:
		spremenljivke[spremenljivka] = vrednost
	return vrednost

def izgradi(izraz: str) -> IzraznoDrevo:
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
		if prev.isnumeric():
			if curr.isalpha():
				# 2a
				predproc_str = predproc_str[:i] + '*' + predproc_str[i:]
			if curr == '(':
				# 2(...)
				predproc_str = predproc_str[:i] + '*' + predproc_str[i:]
		elif curr == '(' and prev.isalpha():
			# a(...)
			predproc_str = predproc_str[:i] + '*' + predproc_str[i:]
		elif prev == ')':
			if not curr.isnumeric() and not curr in ignore:
				# (...)a
				predproc_str = predproc_str[:i] + '*' + predproc_str[i:]
			if curr.isnumeric():
				# (...)2
				predproc_str = predproc_str[:i] + '*' + predproc_str[i:]
		i += 1

	return predproc_str

def aditivni(izraz: str) -> Seštevanje:
	plus  = poišči(izraz, '+')
	minus = poišči(izraz, '-')

	if plus == -1 and minus == -1:
		# ni ne '+', ne '-'
		return multiplikativni(izraz)
	elif plus > minus:
		# '+' ima prednost
		return Seštevanje(aditivni(izraz[:plus]), multiplikativni(izraz[plus+1:]))
	elif minus > plus:
		# '-' ima prednost 
		if minus == 0:
			# negacija na začetku izraza
			return multiplikativni(izraz)
		elif izraz[minus-1] in operatorji:
			# negacija
			return operatorji[izraz[minus-1]](aditivni(izraz[:minus-1]), multiplikativni(izraz[minus:]))
		else:
			# odštevanje
			return Odštevanje(aditivni(izraz[:minus]), multiplikativni(izraz[minus+1:]))

def multiplikativni(izraz: str) -> float:
	krat    = poišči(izraz, '*')
	deljeno = poišči(izraz, '/')

	if krat == -1 and deljeno == -1:
		# ni ne '+', ne'/'
		return potenčni(izraz)
	elif krat > deljeno:
		# '*' ima prednost
		return Množenje(multiplikativni(izraz[:krat]), potenčni(izraz[krat+1:]))
	elif deljeno > krat:
		# '/' ima prednost
		return Deljenje(multiplikativni(izraz[:deljeno]), potenčni(izraz[deljeno+1:]))

def potenčni(izraz: str) -> Potenca:
	na = poišči(izraz, '^')

	if na == -1:
		# ni znaka '^'
		return osnovni(izraz)
	return Potenca(potenčni(izraz[:na]), potenčni(izraz[na+1:]))

def osnovni(izraz: str) -> float:
	if len(izraz) == 0:
		return Str(0.0)
	if izraz[0] == '(':
		return aditivni(izraz[1:-1])

	try:
		return Str(float(izraz))
	except Exception:
		if izraz in konstante:
			return Str(konstante[izraz])
		elif izraz in spremenljivke:
			return Spremenljivka(izraz)
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
