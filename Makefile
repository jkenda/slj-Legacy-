COMPILER := src/compiler.py
LEVEL := 2

all: bool če opti praštevila test

bool: $(COMPILER) primeri/bool.txt
	$(COMPILER) primeri/bool.txt bin/bool.as $(LEVEL)

če: $(COMPILER) primeri/če.txt
	$(COMPILER) primeri/če.txt bin/če.as $(LEVEL)

opti: $(COMPILER) primeri/opti.txt
	$(COMPILER) primeri/opti.txt bin/opti.as $(LEVEL)

praštevila: $(COMPILER) primeri/praštevila.txt
	$(COMPILER) primeri/praštevila.txt bin/praštevila.as $(LEVEL)

test: $(COMPILER) primeri/test.txt
	$(COMPILER) primeri/test.txt bin/test.as $(LEVEL)

exec: src/exec.cpp
	g++ -O2 -g -o exec src/exec.cpp
