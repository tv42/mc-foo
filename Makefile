# make -f DIR/Makefile src=DIR [TARGETS..]

srcdir:=.
VPATH:=.:$(srcdir)

all: default

BINDIR := /usr/bin
DATADIR := /var/lib/mc-foo
DOCDIR := /usr/share/doc/mc-foo
CACHEDIR := /var/cache/mc-foo
LIBDIR := /usr/lib/mc-foo/lib
CACHERS := /usr/lib/mc-foo/lib/cachers
CMDDIR := /usr/lib/mc-foo/commands

SOURCE:=lib/child-bearer.c lib/poller.c lib/nonblock.c lib/split_to_lines.c \
	dj/cache.c dj/dj.c dj/playqueue.c \
	dj/tcp_server.c dj/tcp_listener.c \
	dj/song_input.c dj/song_output.c \
	file-cache/cacher.c dj/prof_write.c dj/prof_read.c \
	dj/playqueue.h dj/prof_write.h dj/prof_read.h dj/tcp_listener.h \
	dj/tcp_server.h dj/song_input.h dj/song_output.h dj/cache.h \
	lib/split_to_lines.h lib/poller.h lib/child-bearer.h lib/nonblock.h

INCLUDES := -Ilib
DEPFILES := $(patsubst %.c,%.d, $(filter %.c, $(SOURCE)))

CFLAGS_VPATH := \
	$(patsubst -I%,-I./%,$(INCLUDES)) \
	$(patsubst -I%,-I$(srcdir)/%,$(INCLUDES)) \
	$(filter -I/%,$(INCLUDES)) \
	$(filter-out -I%,$(INCLUDES))

CFLAGS := -O2 -g \
	-Wall -Werror \
	-Winline -Wredundant-decls -Wnested-externs -Wstrict-prototypes \
	-Waggregate-return -Wpointer-arith \
	$(CFLAGS_VPATH)

BINS := dj/dj file-cache/cacher

CXREF_DIR := cxref

ifdef src
 cxref cxref/%:
	test -d "$(src)"
	cd "$(src)" && make src="" CXREF_DIR="$(CURDIR)/$(CXREF_DIR)" "$@"

 default install %:
	test -d "$(src)"
	make src="" -I "$(src)" -f "$(src)/Makefile" srcdir="$(src)" "$@"
else
 ifeq ($(DEPFILES),$(wildcard $(DEPFILES)))
  include $(DEPFILES)
  default: build
 else
  default: dep build
 endif
 include Makefile.rules
 include Makefile.deps
endif

.PHONY: default all cxref install
