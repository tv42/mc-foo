default: all

OBJ := dj/cache.o dj/child-bearer.o dj/dj.o dj/playqueue.o \
	dj/tcp_server.o dj/tcp_listener.o dj/poller.o
CFLAGS := -g -Wall -O2

all: $(OBJ) dj/dj

clean:
	rm -f $(OBJ) dj/test.o

test: dj/test

%.o: %.c
	gcc -c $(CFLAGS) -o $@ $<

dj/dj: dj/dj.o dj/tcp_listener.o dj/poller.o dj/tcp_server.o

dj/test: dj/test.o dj/playqueue.o
	gcc $(CFLAGS) -o $@ $^

dj/test.o: dj/test.c dj/playqueue.h

.PHONY: default all clean
