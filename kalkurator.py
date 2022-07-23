#!/usr/bin/python3

from operator import add, sub, mul, truediv

operatorji = { '+': add, '-': sub, '*': mul, '/': truediv, '^': pow }
ignore = { '+', '-', '*', '/', '^', ')' }


def main():
	izraz = "\0"
	while izraz != "":
		izraz = input("> ")
		try:
			print("=", ovrednoti(izraz))
		except Exception as e:
			print(e)


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
		if prev.isnumeric() and not curr.isnumeric() and not curr in ignore:
			predproc_str = predproc_str[:i] + '*' + predproc_str[i:]
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

	if krat == -1 and deljeno == -1:
		# ni ne '+', ne'/'
		return potenčni(izraz)
	elif krat > deljeno:
		# '*' ima prednost
		return multiplikativni(izraz[:krat]) * potenčni(izraz[krat+1:])
	elif deljeno > krat:
		# '/' ima prednost
		return multiplikativni(izraz[:deljeno]) / potenčni(izraz[deljeno+1:])

def potenčni(izraz: str) -> float:
	na = poišči(izraz, '^')

	if na == -1:
		# ni znaka '^'
		return osnovni(izraz)
	else:
		return potenčni(izraz[:na]) ** potenčni(izraz[na+1:])

def osnovni(izraz: str) -> float:
	# print(izraz)
	if len(izraz) == 0:
		return 0
	if izraz[0] == '(':
		return aditivni(izraz[1:-1])

	return float(izraz)

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
		raise Exception("Oklepaji se je ujemajo.")

	return -1

if __name__ == "__main__":
	main()
