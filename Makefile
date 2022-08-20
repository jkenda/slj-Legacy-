COMPILER := src/compiler.py
LEVEL := 2

all: bool če opti praštevila test

bool: $(COMPILER) primeri/bool.slj
	$(COMPILER) primeri/bool.slj bin/bool.as $(LEVEL)

če: $(COMPILER) primeri/če.slj
	$(COMPILER) primeri/če.slj bin/če.as $(LEVEL)

opti: $(COMPILER) primeri/opti.slj
	$(COMPILER) primeri/opti.slj bin/opti.as $(LEVEL)

praštevila: $(COMPILER) primeri/praštevila.slj
	$(COMPILER) primeri/praštevila.slj bin/praštevila.as $(LEVEL)

rekurzija: $(COMPILER) primeri/rekurzija.slj
	$(COMPILER) primeri/rekurzija.slj bin/rekurzija.as $(LEVEL)

test: $(COMPILER) primeri/test.slj
	$(COMPILER) primeri/test.slj bin/test.as $(LEVEL)

exec: src/exec.cpp
	g++ -O2 -g -o exec src/exec.cpp
