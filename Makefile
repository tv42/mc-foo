default: all

OBJ := dj/cache.o dj/child-bearer.o dj/dj.o dj/playqueue.o

all: $(OBJ)

clean:
	rm -f $(OBJ)

.PHONY: default all clean
