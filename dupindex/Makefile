#
# Note: use gmake
#

PROGRAM    = bin/dupindex.exe
SRC_CPP    = $(wildcard *.cpp)
OBJECTS    = $(SRC_CPP:.cpp=.o)

all: clean $(PROGRAM)

$(PROGRAM): $(SRC_CPP)
	g++ -O2 -o $@ $<

clean:
	rm $(PROGRAM) || echo ""
