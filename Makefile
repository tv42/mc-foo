default: all

BINDIR := /usr/bin
DATADIR := /var/lib/mc-foo
DOCDIR := /usr/share/doc/mc-foo
CACHEDIR := /var/cache/mc-foo

OBJ := dj/cache.o dj/child-bearer.o dj/dj.o dj/playqueue.o \
	dj/tcp_server.o dj/tcp_listener.o dj/poller.o \
	dj/song_input.o dj/nonblock.o turntable/turntable.o \
	turntable/error.o dj/song_output.o turntable/sigchild.o
CFLAGS := -g -Wall -O2

all: dj/dj turntable/turntable

clean:
	rm -f $(OBJ) dj/test.o

install: all
	install -d -m0755 $(DESTDIR)$(BINDIR)
	install -d -m0755 $(DESTDIR)$(DATADIR)
	install -d -m0755 $(DESTDIR)$(DOCDIR)
	install -d -m0755 $(DESTDIR)$(CACHEDIR)
	install -m0755 dj/dj \
		pick-a-song/pick-a-song \
		remember-profiles/remember-profiles \
		turntable/turntable \
		update-cache \
		$(DESTDIR)$(BINDIR)
	install -d -m0755 $(DESTDIR)$(CACHEDIR)/mediaprofiles \
		$(DESTDIR)$(CACHEDIR)/mediaprofiles/file \
		$(DESTDIR)$(CACHEDIR)/weights \
		$(DESTDIR)$(DATADIR)/media \
		$(DESTDIR)$(DATADIR)/media/file \
		$(DESTDIR)$(DATADIR)/profiles
	@echo 'Now you should create a user for MC Foo, '
	@echo 'preferably named "mcfoo", and run'
	@echo "chown -R mcfoo $(DATADIR) $(CACHEDIR)"

%.o: %.c
	gcc -c $(CFLAGS) -o $@ $<

turntable/turntable: turntable/turntable.o turntable/error.o \
	turntable/sigchild.o

dj/dj: dj/dj.o dj/tcp_listener.o dj/poller.o dj/tcp_server.o \
	dj/song_input.o dj/playqueue.o dj/child-bearer.o \
	dj/nonblock.o dj/song_output.o

.PHONY: default all clean install
