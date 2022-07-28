#!/usr/bin/python3

from ast import arg
from curses.ascii import isspace
from io import TextIOWrapper
import re
import sys
from IzraznoDrevo import *

REGEX_SPR = r"[a-zA-Z_]\w*"
REZERVIRANE_BESEDE = { "natisni", "resnica", "laž", "če", "čene" }

ŠTEVILSKI = { 
	'+': Seštevanje, 
	'-': Odštevanje, 
	'*': Množenje, 
	'/': Deljenje, 
	'%': Modulo,
	'^': Potenca 
}

PRIREJALNI = { 
	'+=': Seštevanje, 
	'-=': Odštevanje, 
	'*=': Množenje, 
	'/=': Deljenje, 
	'%=': Modulo,
	'^=': Potenca 
}

PRIMERJALNI = {
	'==': Enako,
	'>' : Večje,
	'>=': VečjeEnako,
	'<' : Manjše,
	'<=': ManjšeEnako,
}

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

	št_vrstic_neoptimizirano = len(korenski_okvir.optimiziran(0).prevedi().split('\n'))
	
	for nivo in range(1, optimizacija+1):
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
	return Okvir(zap, len(naslovi_spr))

def zaporedje(izraz: str, naslovi_staršev: dict[str, int], naslovi_spr: dict[str, int]) -> Zaporedje:
	izraz = izraz.strip()
	if not izraz or izraz.isspace():
		return Prazno()

	i_locila = max(poišči(izraz, '\n'), poišči(izraz, ';'))

	zadnji_stavek = izraz[i_locila+1:].split('#')[0].strip()

	if i_locila == -1:
		return stavek(zadnji_stavek, naslovi_staršev, naslovi_spr)

	return Zaporedje(zaporedje(izraz[:i_locila], naslovi_staršev, naslovi_spr), stavek(zadnji_stavek, naslovi_staršev, naslovi_spr))

def stavek(izraz: str, naslovi_staršev: dict[str, int], naslovi_spr: dict[str, int]) -> Prirejanje:
	vsi_naslovi = naslovi_staršev | naslovi_spr
	operator: Izraz = None
	razdeljen = ""

	operatorji = list(PRIREJALNI.keys())
	lokacije = [ poišči(izraz, op) for op in operatorji ]

	# poišči lokacijo zadnjega operatorja
	lokacija = max(lokacije)

	if lokacija != -1:
		razdeljen = [izraz[:lokacija], izraz[lokacija+2:]]
		operator = PRIREJALNI[operatorji[lokacije.index(lokacija)]]
	elif izraz.startswith("natisni(") and izraz.endswith(")"):
		notranji_izraz = izraz[len("natisni(") : -len(")")]
		return Natisni(argumenti(notranji_izraz, vsi_naslovi))
	elif izraz.startswith("če") and izraz.endswith("}"):
		return pogojni_stavek(izraz, vsi_naslovi)
	elif izraz.startswith("dokler") and izraz.endswith("}"):
		return zanka(izraz, vsi_naslovi)
	else:
		st_enacajev = izraz.count('=')
		if st_enacajev == 1:
			razdeljen = izraz.split("=")
		else:
			raise Exception(f"Neveljaven izraz: '{izraz}'")

	razdeljen[0] = razdeljen[0].strip()
	razdeljen[1] = razdeljen[1].strip()

	if re.fullmatch(REGEX_SPR, razdeljen[0]):
		ime = razdeljen[0]

		if ime not in konstante:
			naslov = vsi_naslovi.get(ime)
			
			if naslov == None:
				naslovi_spr[ime] = len(vsi_naslovi)
				vsi_naslovi = naslovi_staršev | naslovi_spr

			print(naslovi_staršev, naslovi_spr, razdeljen[0])
			
			drev = drevo(razdeljen[1], vsi_naslovi)

			if (operator != None): 
				drev = operator(Spremenljivka(ime, vsi_naslovi[ime]), drev)

			return Prirejanje(Spremenljivka(ime, vsi_naslovi[ime]), drev)
		else:
			raise Exception(f"'{ime}' je konstanta.")
	else:
		raise Exception(f"Neveljavno ime: '{razdeljen[0]}'")

def pogojni_stavek(izraz: str, naslovi_spr: dict[str, int]) -> PogojniStavek:
	čene = poišči(izraz, "čene")
	pogoj_resnica = izraz
	laž = "{}"
	if čene != -1:
		pogoj_resnica = izraz[:čene]
		laž = izraz[čene+len("čene"):]

	oklepaj  = poišči(pogoj_resnica, '{')
	zaklepaj = poišči(pogoj_resnica, '}')

	pogoj = pogoj_resnica[len("če"):oklepaj]
	resnica = pogoj_resnica[oklepaj+1:zaklepaj]

	oklepaj = poišči(laž, '{')
	zaklepaj = poišči(laž, '}')
	laž = laž[oklepaj+1:zaklepaj]

	return PogojniStavek(
		drevo(pogoj, naslovi_spr),
		okvir(resnica, naslovi_spr),
		okvir(laž, naslovi_spr)
	)

def zanka(izraz: str, naslovi_spr: dict[str, int]) -> Zanka:
	oklepaj  = poišči(izraz, '{')
	zaklepaj = poišči(izraz, '}')

	pogoj = izraz[len("dokler"):oklepaj]
	telo = izraz[oklepaj+1:zaklepaj]

	nove_spr = dict()
	pogoj = drevo(pogoj, naslovi_spr)
	telo = zaporedje(telo, naslovi_spr, nove_spr)

	return Okvir(Zanka(pogoj, telo), len(nove_spr))

def drevo(izraz: str, naslovi_spr: dict[str, int]) -> Izraz:
	return disjunktivni(izraz, naslovi_spr)

def disjunktivni(izraz: str, naslovi_spr: dict[str, int]) -> Disjunkcija:
	lokacija = poišči(izraz, '|')

	if lokacija == -1:
		return konjunktivni(izraz, naslovi_spr)

	return Disjunkcija(
		disjunktivni(izraz[:lokacija], naslovi_spr), 
		konjunktivni(izraz[lokacija+1:], naslovi_spr)
	)

def konjunktivni(izraz: str, naslovi_spr: dict[str, int]) -> Konjunkcija:
	lokacija = poišči(izraz, '&')

	if lokacija == -1:
		return primerjalni(izraz, naslovi_spr)

	return Konjunkcija(
		konjunktivni(izraz[:lokacija], naslovi_spr), 
		primerjalni(izraz[lokacija+1:], naslovi_spr)
	)

def primerjalni(izraz: str, naslovi_spr: dict[str, int]) -> Večje | Enako | Disjunkcija:
	operatorji = list(PRIMERJALNI.keys())
	lokacije = [ poišči(izraz, op) for op in operatorji ]

	# poišči lokacijo zadnjega operatorja
	lokacija = max(lokacije)

	if lokacija == -1:
		return aditivni(izraz, naslovi_spr)

	operator = operatorji[lokacije.index(lokacija)]

	return PRIMERJALNI[operator](
		konjunktivni(izraz[:lokacija], naslovi_spr), 
		aditivni(izraz[lokacija+len(operator):], naslovi_spr)
	)

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
		elif izraz[minus-1] in ŠTEVILSKI:
			# negacija
			return ŠTEVILSKI[izraz[minus-1]](
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
	izraz = izraz.strip()

	if len(izraz) == 0:
		return Prazno()
	if izraz == "resnica":
		return Resnica()
	if izraz == "laž":
		return Laž()
	
	if izraz.startswith("!"):
		return Zanikaj(drevo(izraz[1:], naslovi_spr))
	if izraz.startswith("(") and izraz.endswith(")"):
		return drevo(izraz[1:-1], naslovi_spr)
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

def argumenti(izraz: str, naslovi_spr: dict[str, int]) -> Zaporedje:
	if len(izraz) == 0:
		return Prazno()

	i_vejice = poišči(izraz, ',')
	argument = izraz[i_vejice+1:].strip()

	if i_vejice == -1:
		return drevo(argument, naslovi_spr)

	return Zaporedje(
		drevo(argument, naslovi_spr),
		argumenti(izraz[:i_vejice], naslovi_spr)
	)


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
	navadnih_oklepajev = 0
	zavitih_oklepajev = 0
	znotraj_navedic = False

	i = len(izraz) - 1
	while i >= 0:
		if izraz[i] == '(':
			navadnih_oklepajev -= 1
		elif izraz[i] == '{':
			zavitih_oklepajev -= 1
		elif izraz[i] == '"':
			znotraj_navedic = not znotraj_navedic

		# iskani niz ni znotraj oklepajev ali navednic
		if (
			navadnih_oklepajev == 0 and zavitih_oklepajev == 0 
			and not znotraj_navedic and izraz[i:].startswith(niz)
		):
			if i in [0, len(izraz)-1]:
				return i
			cl = izraz[i-1]; cr = izraz[i+len(niz)]
			if (
				(cl.isspace() or cl.isalnum() or cl in ['(', ')', '"', '}']) and
				(cr.isspace() or cr.isalnum() or cr in ['(', ')', '"', '}'])
			):
				return i

		if izraz[i] == ')':
			navadnih_oklepajev += 1
		elif izraz[i] == '}':
			zavitih_oklepajev += 1

		i -= 1

	if navadnih_oklepajev != 0:
		raise Exception("Oklepaji se ne ujemajo.")

	return -1

if __name__ == "__main__":
	exit((main(len(sys.argv), sys.argv)))
