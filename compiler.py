#!/usr/bin/python3

from ast import arg
from curses.ascii import isspace
from io import TextIOWrapper
import re
import sys
from IzraznoDrevo import *

operatorji = { '+': Seštevanje, '-': Odštevanje, '*': Množenje, '/': Deljenje, '^': Potenca }
ignoriraj = { '+', '-', '*', '/', '^', ')' }
regex_spremenljivk = r"[a-zA-Z_]\w*"

konstante = {
	"e":   2.7182818284590452354,
	"pi":  3.14159265358979323846,
	"phi": 1.61803398874989485,
	"psi": 1.46557123187676802665,
	"mu":  1.84775906502257351225,
	"K":   0.11494204485329620070,
}


def main(argc: int, argv: list[str]) -> int:
	if argc == 3:
		optimizacija = 0
	elif argc == 4:
		optimizacija = int(argv[3])

	with open(argv[1], "r") as file:
#		try:
			vsebina = file.read()
			korenski_okvir = okvir(vsebina, dict())
#		except Exception as e:
#			print(e)
#			return 2

	print(korenski_okvir.drevo())

	št_vrstic_neoptimizirano = len(korenski_okvir.prevedi().split('\n'))
	
	for nivo in range(optimizacija+1):
		print(f"NIVO {nivo}:")
		optimiziran = korenski_okvir.optimiziran(nivo)
		if optimiziran != korenski_okvir:
			korenski_okvir = optimiziran
		else:
			print("/")
		print()

	if optimizacija > 0:
		print(korenski_okvir.drevo())

	assembler = korenski_okvir.prevedi()
	razmerje = len(assembler.split('\n')) / št_vrstic_neoptimizirano
	print("optimizirano / neoptimizirano:", round(razmerje * 100), "%")

	with open(argv[2], "w") as file:
		file.write(assembler)

def okvir(izraz: str, naslovi_staršev: dict[str, int]) -> Okvir:
	naslovi_spr = dict()
	zap = zaporedje(izraz, naslovi_staršev, naslovi_spr)
	return Okvir(zap)

def zaporedje(izraz: str, naslovi_staršev: dict[str, int], naslovi_spr: dict[str, int]) -> Zaporedje:
	izraz = izraz.strip()
	if not izraz or izraz.isspace():
		return Prazno()

	i_locila = max(poišči(izraz, '\n'), poišči(izraz, ';'))

	zadnji_stavek = izraz[i_locila+1:].split('#')[0].strip()

	if i_locila == -1:
		return stavek(zadnji_stavek, naslovi_staršev, naslovi_spr)

	return Zaporedje(zaporedje(izraz[:i_locila], naslovi_staršev, naslovi_spr), stavek(zadnji_stavek, naslovi_staršev, naslovi_spr))

def stavek(izraz: str, naslovi_staršev: dict[str, int], naslovi_spr: dict[str, int]) -> Priredba:
	operator: Izraz = None
	razdeljen = ""

	if izraz.rfind("+=") != -1:
		razdeljen = izraz.split("+=")
		operator  = Seštevanje
	elif izraz.rfind("-=") != -1:
		razdeljen = izraz.split("-=")
		operator  = Odštevanje
	elif izraz.rfind("*=") != -1:
		razdeljen = izraz.split("*=")
		operator  = Množenje
	elif izraz.rfind("/=") != -1:
		razdeljen = izraz.split("/=")
		operator  = Deljenje
	elif izraz.rfind("%=") != -1:
		razdeljen = izraz.split("%=")
		operator  = Modulo
	elif izraz.rfind("^=") != -1:
		razdeljen = izraz.split("^=")
		operator  = Potenca
	elif izraz.startswith("natisni(") and izraz.endswith(")"):
		notranji_izraz = izraz[len("natisni(") : -len(")")]
		return Natisni(*argumenti(notranji_izraz, naslovi_spr))
	else:
		st_enacajev = izraz.count('=')
		if st_enacajev == 1:
			razdeljen = izraz.split("=")
		else:
			raise Exception(f"Neveljaven izraz: '{izraz}'")

	razdeljen[0] = razdeljen[0].strip()
	razdeljen[1] = razdeljen[1].strip()

	if re.fullmatch(regex_spremenljivk, razdeljen[0]):
		ime = razdeljen[0]

		if ime not in konstante:
			nova_spr = False
			pozicija = naslovi_spr.get(ime)
			
			if pozicija == None:
				naslovi_spr[ime] = len(naslovi_spr)
				nova_spr = True
			
			drev = drevo(razdeljen[1], naslovi_staršev | naslovi_spr)

			if (operator != None): 
				drev = operator(Spremenljivka(ime, naslovi_spr[ime]), drev)

			return Priredba(Spremenljivka(ime, naslovi_spr[ime]), drev, nova_spr)
		else:
			raise Exception(f"'{ime}' je konstanta.")
	else:
		raise Exception(f"Neveljavno ime: '{razdeljen[0]}'")


def drevo(izraz: str, naslovi_spr: dict[str, int]) -> Izraz:
	return aditivni(predprocesiran(izraz), naslovi_spr)

def aditivni(izraz: str, naslovi_spr: dict[str, int]) -> Seštevanje:
	plus  = poišči(izraz, '+')
	minus = poišči(izraz, '-')

	if plus == -1 and minus == -1:
		# ni ne '+', ne '-'
		return multiplikativni(izraz, naslovi_spr)
	elif plus > minus:
		# '+' ima prednost
		return Seštevanje(aditivni(izraz[:plus], naslovi_spr), 
						  multiplikativni(izraz[plus+1:], naslovi_spr))
	elif minus > plus:
		# '-' ima prednost 
		if minus == 0:
			# negacija na začetku izraza
			return multiplikativni(izraz, naslovi_spr)
		elif izraz[minus-1] in operatorji:
			# negacija
			return operatorji[izraz[minus-1]](
				aditivni(izraz[:minus-1], naslovi_spr), 
				multiplikativni(izraz[minus:], naslovi_spr)
			)
		else:
			# odštevanje
			return Odštevanje(aditivni(izraz[:minus], naslovi_spr), 
							  multiplikativni(izraz[minus+1:], naslovi_spr))

def multiplikativni(izraz: str, naslovi_spr: dict[str, int]) -> float:
	krat    = poišči(izraz, '*')
	deljeno = poišči(izraz, '/')
	modulo  = poišči(izraz, '%')

	if krat == -1 and deljeno == -1 and modulo == -1:
		# ni ne '+', ne'/', ne '%
		return potenčni(izraz, naslovi_spr)
	elif krat > deljeno and krat > modulo:
		# '*' ima prednost
		return Množenje(multiplikativni(izraz[:krat], naslovi_spr), potenčni(izraz[krat+1:], naslovi_spr))
	elif deljeno > krat and deljeno > modulo:
		# '/' ima prednost
		return Deljenje(multiplikativni(izraz[:deljeno], naslovi_spr), potenčni(izraz[deljeno+1:], naslovi_spr))
	elif modulo > krat and modulo > deljeno:
		# '%' ima prednost
		return Modulo(multiplikativni(izraz[:modulo], naslovi_spr), potenčni(izraz[modulo+1:], naslovi_spr))

def potenčni(izraz: str, naslovi_spr: dict[str, int]) -> Potenca:
	na = poišči(izraz, '^')

	if na == -1:
		# ni znaka '^'
		return osnovni(izraz, naslovi_spr)
	return Potenca(potenčni(izraz[:na], naslovi_spr), potenčni(izraz[na+1:], naslovi_spr))

def osnovni(izraz: str, naslovi_spr: dict[str, int]) -> float:
	if len(izraz) == 0:
		return Prazno()
	if izraz.startswith("(") and izraz.endswith(")"):
		return aditivni(izraz[1:-1], naslovi_spr)
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

def argumenti(izraz: str, naslovi_spr: dict[str, int]) -> tuple:
	if len(izraz) == 0:
		return Prazno()

	i_vejice = poišči(izraz, ',')

	vozlišče: Vozlišče
	argument = izraz[i_vejice+1:].strip()

	vozlišče = drevo(argument, naslovi_spr)

	if i_vejice == -1:
		return (vozlišče, 1)

	zap, st_arg = argumenti(izraz[:i_vejice], naslovi_spr)
	return (Zaporedje(vozlišče, zap), st_arg + 1)


def predprocesiran(izraz: str) -> str:
	# odstrani presledke
	predproc_str = ""
	med_navednicami = False
	for char in izraz:
		if char == '"':
			med_navednicami = not med_navednicami
		if med_navednicami or not char.isspace():
			predproc_str += char

	# dodaj znak '*' v implicitno množenje
	i = 1
	dolzina = len(predproc_str)
	while i < dolzina:
		prev = predproc_str[i-1]; curr = predproc_str[i]
		vstavi_krat = False
		if prev == ')' and curr == '(':
			# )(
			vstavi_krat = True
		if prev.isnumeric():
			# 2a, 2(...)
			if curr.isalpha() or curr == '(':
				vstavi_krat = True
		elif prev == ')':
				# (...)a, (...)2
			if curr.isalpha() or curr.isnumeric():
				vstavi_krat = True
			
		if vstavi_krat:
			predproc_str = predproc_str[:i] + '*' + predproc_str[i:]
			dolzina += 1
			i += 1
		i += 1

	return predproc_str

def poišči(izraz: str, niz: str) -> int:
	oklepajev = 0
	znotraj_navedic = False

	i = len(izraz) - 1
	while i >= 0:
		if izraz[i] == ')':
			oklepajev += 1
		elif izraz[i] == '(':
			oklepajev -= 1
		elif izraz[i] == '"':
			znotraj_navedic = not znotraj_navedic

		if oklepajev == 0 and not znotraj_navedic and izraz[i:].startswith(niz):
			# iskani znak ni znotraj oklepajev
			return i
		i -= 1

	if oklepajev != 0:
		raise Exception("Oklepaji se ne ujemajo.")

	return -1

if __name__ == "__main__":
	exit((main(len(sys.argv), sys.argv)))
