#!/usr/bin/python3

from io import TextIOWrapper
import re
import sys
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

naslovi_spr = dict()
spr_vrednosti = dict()

def main(argc: int, argv: list[str]) -> int:
	if argc != 3:
		return 1

	with open(argv[1], "r") as file:
#		try:
		prog = scope(file)
#		except Exception as e:
#			print(e)
#			return 2

	ukazi = prog.compile(len(naslovi_spr))
	prog.print()
	print(naslovi_spr)

	with open(argv[2], "w") as file:
		file.write(ukazi)

def scope(file: TextIOWrapper) -> Scope:
	vrstice = filter(lambda v : v and not v.isspace(), file.readlines())
	vrstice = map(lambda v : v.strip(), vrstice)
	vrstice = list(vrstice)
	return Scope(zaporedje(vrstice))

def zaporedje(vrstice: list[str]) -> Zaporedje:
	if len(vrstice) == 0:
		return Prazno()
	if len(vrstice) == 1:
		return priredba(vrstice[0])
	if len(vrstice) == 2:
		return Zaporedje(priredba(vrstice[0]), priredba(vrstice[1]))

	return Zaporedje(zaporedje(vrstice[:-1]), priredba(vrstice[-1]))

def priredba(izraz: str) -> Priredba:
	st_enacajev = izraz.count('=')

	if st_enacajev == 1:
		razdeljen = list(map(lambda x: x.strip(), izraz.split('=')))
		if re.fullmatch(var_regex, razdeljen[0]):
			if razdeljen[0] not in konstante:
				ime = razdeljen[0]
				izrazno_drevo = drevo(razdeljen[1])

				pozicija = naslovi_spr.get(ime)
				if pozicija != None:
					return Priredba(Spremenljivka(ime, naslovi_spr[ime]), izrazno_drevo, False)
				else:
					naslovi_spr[ime] = len(naslovi_spr)
					return Priredba(Spremenljivka(ime, naslovi_spr[ime]), izrazno_drevo, True)
			else:
				raise Exception(f"'{ime}' je konstanta.")
		else:
			raise Exception(f"Neveljavno ime: '{razdeljen[0]}'")
			
	if izraz.startswith("print(") and izraz.endswith(")"):
		notranji_izraz = izraz[len("print(") : -len(")")]
		argumenti = notranji_izraz.split(",")
		return Print([ aditivni(arg.strip()) for arg in argumenti ])
	else:
		raise Exception(f"Neveljaven izraz: '{izraz}'")


def drevo(izraz: str) -> Izraz:
	return aditivni(predprocesiran(izraz))

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
		return Prazno()
	if izraz.startswith("(") and izraz.endswith(")"):
		return aditivni(izraz[1:-1])
	if izraz.startswith('"') and izraz.endswith('"'):
		return Niz(izraz[1:-1])

	try:
		return Število(float(izraz))
	except Exception:
		if izraz in konstante:
			return Število(konstante[izraz])
		elif izraz in naslovi_spr:
			return Spremenljivka(izraz, naslovi_spr[izraz])
		else:
			raise Exception(f"'{izraz}' ni definiran.")


def predprocesiran(izraz: str) -> str:
	# odstrani presledke
	predproc_str = re.sub(r"\s+", "", izraz)

	# dodaj znak '*' v implicitno množenje
	i = 1
	dolzina = len(predproc_str)
	while i < dolzina:
		prev = predproc_str[i-1]; curr = predproc_str[i]
		if prev.isnumeric():
			if curr.isalpha():
				# 2a
				predproc_str = predproc_str[:i] + '*' + predproc_str[i:]
				dolzina += 1
			if curr == '(':
				# 2(...)
				predproc_str = predproc_str[:i] + '*' + predproc_str[i:]
				dolzina += 1
		elif prev == ')':
			if not curr.isnumeric() and not curr in ignore:
				# (...)a
				predproc_str = predproc_str[:i] + '*' + predproc_str[i:]
				dolzina += 1
			if curr.isnumeric():
				# (...)2
				predproc_str = predproc_str[:i] + '*' + predproc_str[i:]
				dolzina += 1
		i += 1

	return predproc_str

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
	exit((main(len(sys.argv), sys.argv)))
