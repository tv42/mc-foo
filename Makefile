default: all

OBJ := dj/cache.o dj/child-bearer.o dj/dj.o dj/playqueue.o \
	dj/tcp_server.o dj/tcp_listener.o dj/poller.o \
	dj/song_input.o dj/nonblock.o turntable/turntable.o \
	turntable/error.o dj/song_output.o turntable/sigchild.o
CFLAGS := -g -Wall -O2

all: dj/dj turntable/turntable

clean:
	rm -f $(OBJ) dj/test.o

test: dj/test

%.o: %.c
	gcc -c $(CFLAGS) -o $@ $<

turntable/turntable: turntable/turntable.o turntable/error.o \
	turntable/sigchild.o

dj/dj: dj/dj.o dj/tcp_listener.o dj/poller.o dj/tcp_server.o \
	dj/song_input.o dj/playqueue.o dj/child-bearer.o \
	dj/nonblock.o dj/song_output.o

dj/test: dj/test.o dj/playqueue.o
	gcc $(CFLAGS) -o $@ $^

dj/test.o: dj/test.c dj/playqueue.h

.PHONY: default all clean
