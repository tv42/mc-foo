default: all

BINDIR := /usr/bin
DATADIR := /var/lib/mc-foo
DOCDIR := /usr/share/doc/mc-foo
CACHEDIR := /var/cache/mc-foo
LIBDIR := /usr/lib/mc-foo/lib
CMDDIR := /usr/lib/mc-foo/commands

LIBOBJ:=lib/child-bearer.o lib/poller.o lib/nonblock.o lib/split_to_lines.o
OBJ := dj/cache.o dj/dj.o dj/playqueue.o \
	dj/tcp_server.o dj/tcp_listener.o \
	dj/song_input.o dj/song_output.o turntable/sigchild.o
CFLAGS := -g -Wall -O2 -Ilib

BINS := dj/dj

all: $(BINS)

clean:
	rm -f $(OBJ) $(LIBOBJ) $(BINS)

install: all
	install -d -m0755 $(DESTDIR)$(BINDIR)
	install -d -m0755 $(DESTDIR)$(DATADIR)
	install -d -m0755 $(DESTDIR)$(DOCDIR)
	install -d -m0755 $(DESTDIR)$(CACHEDIR)
	install -d -m0755 $(DESTDIR)$(LIBDIR)
	install -d -m0755 $(DESTDIR)$(CMDDIR)
	install -m0644 README $(DESTDIR)$(DOCDIR)
	install -m0755 dj/dj \
		commands/[a-z]* $(DESTDIR)$(CMDDIR)
#	install -m0755 turntable/turntable \
#		$(DESTDIR)$(LIBDIR)
	install -m0755 turntable/mpg123-remote \
		$(DESTDIR)$(LIBDIR)/turntable
	install -m0755 libbin/[a-z]* $(DESTDIR)$(LIBDIR)
	install -m0755 bin/[a-z]* $(DESTDIR)$(BINDIR)
	install -d -m0755 $(DESTDIR)$(CACHEDIR)/mediaprofiles \
		$(DESTDIR)$(CACHEDIR)/mediaprofiles/file \
		$(DESTDIR)$(CACHEDIR)/weights \
		$(DESTDIR)$(DATADIR)/media \
		$(DESTDIR)$(DATADIR)/media/file \
		$(DESTDIR)$(DATADIR)/profiles
	@echo 'Now you should create a group for MC Foo, '
	@echo 'preferably named "mcfoo", and run'
	@echo "chgrp -R mcfoo $(DATADIR)/{media,profiles}"
	@echo "chgrp -R mcfoo $(CACHEDIR)/{mediaprofiles,weights}"
	@echo "chmod -R g+s $(DATADIR)/{media,profiles}"
	@echo "chmod -R g+s $(CACHEDIR)/{mediaprofiles,weights}"

%.o: %.c
	gcc -c $(CFLAGS) -o $@ $<

dj/dj: dj/dj.o dj/tcp_listener.o dj/tcp_server.o \
	dj/song_input.o dj/playqueue.o \
	dj/song_output.o dj/prof_read.o \
	lib/split_to_lines.o lib/poller.o \
	lib/child-bearer.o lib/nonblock.o \

.PHONY: default all clean install
