#!/usr/bin/python3

from operator import add, sub, mul, truediv, mod
import re

operatorji = { '+': add, '-': sub, '*': mul, '/': truediv, '%': mod, '^': pow }
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
			izraz = input("> ")
			vrednost = priredi(izraz)
			print("=", vrednost)
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

	vrednost = ovrednoti(izraz)
	if spremenljivka:
		spremenljivke[spremenljivka] = vrednost
	return vrednost

def ovrednoti(izraz: str) -> float:
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
		vstavi_krat = False
		if prev == ')' and curr == '(':
			# )(
			vstavi_krat = True
		if prev.isnumeric():
			# 2a, 2(...)
			if curr.isalpha() or curr == '(':
				vstavi_krat = True
		elif curr == '(' and prev.isalpha():
			# a(...)
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

def aditivni(izraz: str) -> float:
	plus  = poišči(izraz, '+')
	minus = poišči(izraz, '-')

	if plus == -1 and minus == -1:
		# ni ne '+', ne '-'
		return multiplikativni(izraz)
	elif plus > minus:
		# '+' ima prednost
		return aditivni(izraz[:plus]) + multiplikativni(izraz[plus+1:])
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
			return aditivni(izraz[:minus]) - multiplikativni(izraz[minus+1:])

def multiplikativni(izraz: str) -> float:
	krat    = poišči(izraz, '*')
	deljeno = poišči(izraz, '/')
	modulo  = poišči(izraz, '%')

	if krat == -1 and deljeno == -1 and modulo == -1:
		# ni ne '+', ne'/'
		return potenčni(izraz)
	elif krat > deljeno and krat > modulo:
		# '*' ima prednost
		return multiplikativni(izraz[:krat]) * potenčni(izraz[krat+1:])
	elif deljeno > krat and deljeno > modulo:
		# '/' ima prednost
		return multiplikativni(izraz[:deljeno]) / potenčni(izraz[deljeno+1:])
	elif modulo > krat and modulo > deljeno:
		# '%' ima prednost
		return multiplikativni(izraz[:deljeno]) % potenčni(izraz[deljeno+1:])

def potenčni(izraz: str) -> float:
	na = poišči(izraz, '^')

	if na == -1:
		# ni znaka '^'
		return osnovni(izraz)
	else:
		return potenčni(izraz[:na]) ** potenčni(izraz[na+1:])

def osnovni(izraz: str) -> float:
	if len(izraz) == 0:
		return 0
	if izraz[0] == '(':
		return aditivni(izraz[1:-1])

	try:
		return float(izraz)
	except Exception:
		try:
			return (konstante | spremenljivke)[izraz]
		except:
			raise Exception(f"'{izraz}' not defined.")

def poišči(izraz: str, char: str) -> int:
	oklepajev = 0

	i = len(izraz) - 1
	while i >= 0:
		if izraz[i] == ')':
			oklepajev += 1
		elif izraz[i] == '(':
			oklepajev -= 1

		if oklepajev == 0 and izraz[i] == char:
			# iskani znak ni znotraj oklepajev
			return i
		i -= 1

	if oklepajev != 0:
		raise Exception("Oklepaji se ne ujemajo.")

	return -1

if __name__ == "__main__":
	main()
