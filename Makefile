COMPILER := src/compiler.py
LEVEL := 2

all: bool če opti praštevila rekurzija test

bin:
	mkdir bin

bool: $(COMPILER) bin primeri/bool.slj
	$(COMPILER) primeri/bool.slj bin/bool.as $(LEVEL)

če: $(COMPILER) bin primeri/če.slj
	$(COMPILER) primeri/če.slj bin/če.as $(LEVEL)

opti: $(COMPILER) bin primeri/opti.slj
	$(COMPILER) primeri/opti.slj bin/opti.as $(LEVEL)

praštevila: $(COMPILER) bin primeri/praštevila.slj
	$(COMPILER) primeri/praštevila.slj bin/praštevila.as $(LEVEL)

rekurzija: $(COMPILER) bin primeri/rekurzija.slj
	$(COMPILER) primeri/rekurzija.slj bin/rekurzija.as $(LEVEL)

test: $(COMPILER) bin primeri/test.slj
	$(COMPILER) primeri/test.slj bin/test.as $(LEVEL)

exec: src/exec.cpp
	g++ -O2 -g -o exec src/exec.cpp
