
CFLAGS=-g
LDFLAGS=-g

turntable: turntable.o error.o
	gcc $(LDFLAGS) -o turntable turntable.o error.o

.c.o:
	gcc $(CFLAGS) -c $<
