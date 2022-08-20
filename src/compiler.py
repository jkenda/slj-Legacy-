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

spremenljivke_stack: list[dict[str, Spremenljivka]] = []
funkcije_stack: list[dict[str, Funkcija]] = []
spremenljivke: dict[str, Spremenljivka] = {}
funkcije: dict[str, Funkcija] = {}
znotraj_funkcije = False

vrh_stacka = lambda: Zaporedje(*spremenljivke.values()).sprememba_stacka()


def main(argc: int, argv: list[str]) -> int:
	if argc == 3:
		optimizacija = 0
	elif argc == 4:
		optimizacija = int(argv[3])

	with open(argv[1], "r") as file:
#		try:
			vsebina = file.read()
			korenski_okvir = okvir(vsebina)
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

	assembler = postprocesiran(korenski_okvir.prevedi())
	razmerje = len(assembler.split('\n')) / št_vrstic_neoptimizirano
	print("optimizirano / neoptimizirano:", round(razmerje * 100), "%")

	with open(argv[2], "w") as file:
		file.write(assembler)

def okvir(izraz: str) -> Okvir:
	spremenljivke_stack.append({})
	funkcije_stack.append({})

	zap = zaporedje(izraz)

	length  = sum(spr.sprememba_stacka() for spr in spremenljivke_stack[-1].values())
	length += sum(fun.sprememba_stacka() for fun in funkcije_stack[-1].values())

	for ime in spremenljivke_stack[-1].keys():
		del spremenljivke[ime]
	for ime in funkcije_stack[-1].keys():
		del funkcije[ime]
	spremenljivke_stack.pop()

	return Okvir(zap, length)

def zaporedje(izraz: str) -> Zaporedje:
	izrazi: list[Vozlišče] = []

	i_ločila = min(poišči_spredaj(izraz, '\n'), poišči_spredaj(izraz, ';'))
	while i_ločila < len(izraz):
		prvi_stavek = izraz[:i_ločila].split('#')[0].strip()
		if prvi_stavek != "":
			izrazi.append(stavek(prvi_stavek))
		izraz = izraz[i_ločila+1:].strip()
		i_ločila = min(poišči_spredaj(izraz, '\n'), poišči_spredaj(izraz, ';'))

	if izraz != "":
		izrazi.append(stavek(izraz))

	return Zaporedje(*izrazi)

def stavek(izraz: str) -> Prirejanje:
	operator: Izraz = None
	razdeljen = ""

	operatorji = list(PRIREJALNI.keys())
	lokacije = [ poišči_zadaj(izraz, op) for op in operatorji ]

	# poišči lokacijo zadnjega operatorja
	lokacija = max(lokacije)

	if lokacija != -1:
		razdeljen = [izraz[:lokacija], izraz[lokacija+2:]]
		operator = PRIREJALNI[operatorji[lokacije.index(lokacija)]]
	elif izraz.startswith('{') and izraz.endswith('}'):
		return okvir(izraz[1:-1])
	elif izraz.startswith("natisni(") and izraz.endswith(")"):
		notranji_izraz = izraz[len("natisni(") : -len(")")]
		return Natisni(argumenti(notranji_izraz))
	elif izraz.startswith("če") and izraz.endswith("}"):
		return pogojni_stavek(izraz)
	elif izraz.startswith("dokler") and izraz.endswith("}"):
		return zanka(izraz)
	elif izraz.startswith("funkcija") and izraz.endswith("}"):
		return funkcija(izraz)
	elif izraz.startswith("vrni"):
		return Prirejanje(spremenljivke["vrni"], drevo(izraz[len("vrni"):]), znotraj_funkcije)
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
			naslov = spremenljivke.get(ime)
			
			if naslov == None:
				spr = Spremenljivka(ime, vrh_stacka(), znotraj_funkcije)
				spremenljivke_stack[-1][ime] = spr
				spremenljivke[ime] = spr

			drev = drevo(razdeljen[1])

			if (operator != None): 
				drev = operator(spremenljivke[ime], drev)

			return Prirejanje(spremenljivke[ime], drev, znotraj_funkcije)
		else:
			raise Exception(f"'{ime}' je konstanta.")
	else:
		raise Exception(f"Neveljavno ime: '{razdeljen[0]}'")

def pogojni_stavek(izraz: str, ) -> PogojniStavek:
	čene = poišči_spredaj(izraz, "čene")
	pogoj_resnica = izraz
	laž = "{}"
	if čene != -1:
		pogoj_resnica = izraz[:čene]
		laž = izraz[čene+len("čene"):].strip()

	oklepaj  = poišči_spredaj(pogoj_resnica, '{')
	zaklepaj = poišči_zadaj(pogoj_resnica, '}')

	pogoj = pogoj_resnica[len("če"):oklepaj]
	resnica = pogoj_resnica[oklepaj+1:zaklepaj]

	oklepaj = poišči_spredaj(laž, '{')
	zaklepaj = poišči_zadaj(laž, '}')

	return PogojniStavek(
		drevo(pogoj),
		okvir(resnica),
		okvir(laž)
	)

def zanka(izraz: str) -> Zanka:
	izraz = izraz.strip()

	oklepaj  = poišči_zadaj(izraz, '{')
	zaklepaj = poišči_zadaj(izraz, '}')

	pogoj = izraz[len("dokler"):oklepaj]
	telo = izraz[oklepaj+1:zaklepaj]

	nove_spr = {}
	pogoj = drevo(pogoj)
	telo = zaporedje(telo)

	return Okvir(Zanka(pogoj, telo), len(nove_spr))

def funkcija(izraz: str):
	global spremenljivke, spremenljivke_stack, znotraj_funkcije

	args: list[Spremenljivka] = []

	prejšnje_spr = spremenljivke.copy()
	spr_funkcije = {
		"vrni": Spremenljivka("vrni", 0, True),
		"0_PC": Spremenljivka("0_PC", 1, True),
	}

	vrh_stacka = lambda: Zaporedje(*spr_funkcije.values()).sprememba_stacka()

	oklepaj  = poišči_spredaj(izraz, '(')
	zaklepaj = poišči_spredaj(izraz, ')')

	ime_funkcije = izraz[len("funkcija"):oklepaj].strip()

	for argument in map(lambda a: a.strip(), izraz[oklepaj+1:zaklepaj].split(',')):
		if argument not in spr_funkcije:
			spr_funkcije[argument] = Spremenljivka(argument, vrh_stacka(), True)
			args.append(spr_funkcije[argument])
		else:
			raise Exception("Imena argumentov morajo biti unikatna.")

	spr_funkcije["0_OF"] = Spremenljivka("0_OF", vrh_stacka(), True)

	spr_len = len(spr_funkcije)

	fun = Funkcija(ime_funkcije, args, Število(0), 0)
	funkcije_stack[-1][ime_funkcije] = fun
	funkcije[ime_funkcije] = fun

	oklepaj  = poišči_spredaj(izraz, '{')
	zaklepaj = poišči_zadaj(izraz, '}')

	spremenljivke = spr_funkcije
	spremenljivke_stack.append(spr_funkcije)
	znotraj_funkcije = True
	telo = zaporedje(izraz[oklepaj+1:zaklepaj])
	znotraj_funkcije = False

	for spr in spremenljivke.values(): print(str(spr), end=", ")
	print()

	spremenljivke_stack.pop()
	spremenljivke = prejšnje_spr

	fun.telo = telo
	fun.prostor = len(spr_funkcije) - spr_len

	return fun

def funkcijski_klic(izraz: str) -> Zaporedje:
	oklepaj  = poišči_spredaj(izraz, '(')
	zaklepaj = poišči_spredaj(izraz, ')')

	ime = izraz[:oklepaj].strip()
	funkcija = funkcije[ime]

	args = argumenti(izraz[oklepaj+1:zaklepaj])

	return FunkcijskiKlic(funkcija, args)

def drevo(izraz: str) -> Izraz:
	izraz = izraz.strip()

	return disjunktivni(izraz)

def disjunktivni(izraz: str) -> Disjunkcija:
	izraz = izraz.strip()
	lokacija = poišči_zadaj(izraz, '|')

	if lokacija == -1:
		return konjunktivni(izraz)

	return Disjunkcija(
		disjunktivni(izraz[:lokacija]), 
		konjunktivni(izraz[lokacija+1:])
	)

def konjunktivni(izraz: str) -> Konjunkcija:
	lokacija = poišči_zadaj(izraz, '&')

	if lokacija == -1:
		return primerjalni(izraz)

	return Konjunkcija(
		konjunktivni(izraz[:lokacija]), 
		primerjalni(izraz[lokacija+1:])
	)

def primerjalni(izraz: str, ) -> Večje | Enako | Disjunkcija:
	operatorji = list(PRIMERJALNI.keys())
	lokacije = [ poišči_zadaj(izraz, op) for op in operatorji ]

	# poišči lokacijo zadnjega operatorja
	lokacija = max(lokacije)

	if lokacija == -1:
		return aditivni(izraz)

	operator = operatorji[lokacije.index(lokacija)]

	return PRIMERJALNI[operator](
		konjunktivni(izraz[:lokacija]), 
		aditivni(izraz[lokacija+len(operator):])
	)

def aditivni(izraz: str) -> Seštevanje:
	plus  = poišči_zadaj(izraz, '+')
	minus = poišči_zadaj(izraz, '-')

	if plus == -1 and minus == -1:
		# ni ne '+', ne '-'
		return multiplikativni(izraz)
	elif plus > minus:
		# '+' ima prednost
		return Seštevanje(aditivni(izraz[:plus]), 
						  multiplikativni(izraz[plus+1:]))
	elif minus > plus:
		# '-' ima prednost 
		if minus == 0:
			# negacija na začetku izraza
			return multiplikativni(izraz)
		elif izraz[minus-1] in ŠTEVILSKI:
			# negacija
			return ŠTEVILSKI[izraz[minus-1]](
				aditivni(izraz[:minus-1]), 
				multiplikativni(izraz[minus:])
			)
		else:
			# odštevanje
			return Odštevanje(aditivni(izraz[:minus]), 
							  multiplikativni(izraz[minus+1:]))

def multiplikativni(izraz: str) -> float:
	krat    = poišči_zadaj(izraz, '*')
	deljeno = poišči_zadaj(izraz, '/')
	modulo  = poišči_zadaj(izraz, '%')

	if krat == -1 and deljeno == -1 and modulo == -1:
		# ni ne '+', ne'/', ne '%
		return potenčni(izraz)
	elif krat > deljeno and krat > modulo:
		# '*' ima prednost
		return Množenje(multiplikativni(izraz[:krat]), potenčni(izraz[krat+1:]))
	elif deljeno > krat and deljeno > modulo:
		# '/' ima prednost
		return Deljenje(multiplikativni(izraz[:deljeno]), potenčni(izraz[deljeno+1:]))
	elif modulo > krat and modulo > deljeno:
		# '%' ima prednost
		return Modulo(multiplikativni(izraz[:modulo]), potenčni(izraz[modulo+1:]))

def potenčni(izraz: str) -> Potenca:
	na = poišči_zadaj(izraz, '^')

	if na == -1:
		# ni znaka '^'
		return osnovni(izraz)
	return Potenca(potenčni(izraz[:na]), potenčni(izraz[na+1:]))

def osnovni(izraz: str) -> float:
	izraz = izraz.strip()

	if len(izraz) == 0:
		return Prazno()
	if izraz == "resnica":
		return Resnica()
	if izraz == "laž":
		return Laž()

	if izraz.startswith("!"):
		return Zanikaj(drevo(izraz[1:]))
	if izraz.startswith("(") and izraz.endswith(")"):
		return drevo(izraz[1:-1])
	if izraz.startswith('"') and izraz.endswith('"'):
		return Niz(izraz[1:-1])
	
	oklepaj  = poišči_spredaj(izraz, '(')
	ime = izraz[:oklepaj].strip()

	if ime in funkcije:
		return funkcijski_klic(izraz)

	try:
		return Število(float(izraz))
	except Exception:
		if izraz in konstante:
			return Število(konstante[izraz])
		elif izraz in spremenljivke:
			return spremenljivke[izraz]
		else:
			raise Exception(f"'{izraz}' ni definiran.")

def argumenti(izraz: str) -> Zaporedje:
	args: list[Vozlišče] = []

	i_vejice = poišči_spredaj(izraz, ',')
	while i_vejice < len(izraz):
		argument = izraz[:i_vejice].strip()
		args.append(drevo(argument))
		izraz = izraz[i_vejice+1:]
		i_vejice = poišči_spredaj(izraz, ',')

	args.append(drevo(izraz))
	
	return Zaporedje(*args)

def predprocesiran(izraz: str) -> str:
	# odstrani presledke
	predproc_str = ""
	med_navednicami = False
	for char in izraz:
		if char == '"':
			med_navednicami = not med_navednicami
		if med_navednicami or not char.isspace():
			predproc_str += char

	return predproc_str

# nadomesti relativne skoke z absolutnimi
def postprocesiran(ukazi: str) -> str:
	postproc = ""

	vrstice = ukazi.split('\n')
	oznake_funkcij = {}

	i = 0
	while i < len(vrstice):
		if vrstice[i].startswith('.'):
			oznake_funkcij[vrstice[i]] = i
			vrstice.pop(i)
		else:
			i += 1

	for št_vrstice, vrstica in enumerate(vrstice):
		if vrstica == "": continue
		razdeljen = vrstica.split(' ')
		ukaz = razdeljen[0]

		if ukaz in ["JUMP", "JMPC"]:
			if len(razdeljen) == 1:
				postproc += f"{ukaz}\n"
			else:
				if razdeljen[1].startswith('.'):
					ime = razdeljen[1]
					absolutni_skok = oznake_funkcij[ime]
				else:
					relativni_skok = int(razdeljen[1])
					absolutni_skok = št_vrstice + relativni_skok
				postproc += f"{ukaz} #{absolutni_skok}\n"
		elif ukaz == "PC":
			odmik = int(razdeljen[1])
			postproc += f"PUSH #{št_vrstice + odmik}\n"
		else:
			postproc += f"{vrstica}\n"

	return postproc

def poišči_spredaj(izraz: str, niz: str) -> int:
	navadnih_oklepajev = 0
	zavitih_oklepajev = 0
	znotraj_navedic = False

	i = 0
	while i < len(izraz):

		if izraz[i] == ')':
			navadnih_oklepajev -= 1
		elif izraz[i] == '}':
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

		if izraz[i] == '(':
			navadnih_oklepajev += 1
		elif izraz[i] == '{':
			zavitih_oklepajev += 1

		i += 1

	if navadnih_oklepajev != 0:
		raise Exception("Oklepaji se ne ujemajo.")

	return len(izraz)

def poišči_zadaj(izraz: str, niz: str) -> int:
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
