default: all

OBJ := dj/cache.o dj/child-bearer.o dj/dj.o dj/playqueue.o
CFLAGS := -g -Wall

all: $(OBJ)

clean:
	rm -f $(OBJ) dj/test.o

test: dj/test

%.o: %.c
	gcc -c $(CFLAGS) -o $@ $<

dj/test: dj/test.o dj/playqueue.o
	gcc $(CFLAGS) -o $@ $^

dj/test.o: dj/test.c dj/playqueue.h

dj/playqueue.o: dj/playqueue.c dj/playqueue.h

.PHONY: default all clean
