BINDIR := /usr/bin
DATADIR := /var/lib/mc-foo
DOCDIR := /usr/share/doc/mc-foo
CACHEDIR := /var/cache/mc-foo
LIBDIR := /usr/lib/mc-foo/lib
PYLIBDIR := /usr/lib/python2.2/site-packages
CMDDIR := /usr/lib/mc-foo/commands

all:

clean:

realclean: clean
	find lib -name '*.pyc' -print0 | xargs -0 --no-run-if-empty rm

install: all
	install -d -m0755 $(DESTDIR)$(BINDIR)
	install -d -m0755 $(DESTDIR)$(DATADIR)
	install -d -m0755 $(DESTDIR)$(DOCDIR)
	install -d -m0755 $(DESTDIR)$(CACHEDIR) \
		$(DESTDIR)$(CACHEDIR)/file \
		$(DESTDIR)$(CACHEDIR)/file.tmp
	install -d -m0755 $(DESTDIR)$(LIBDIR)
	install -d -m0755 $(DESTDIR)$(PYLIBDIR)
	install -d -m0755 $(DESTDIR)$(CMDDIR)
	install -m0644 README $(DESTDIR)$(DOCDIR)
	install -m0755 commands/[a-z]* $(DESTDIR)$(CMDDIR)
	install -m0755 libbin/[a-z]* $(DESTDIR)$(LIBDIR)
	cd lib && for a in `find . -name '*.py'`; do \
		install -D -m0644 "$$a" "$(DESTDIR)$(PYLIBDIR)/$$a"; \
	done
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
	@echo "chgrp -R mcfoo $(CACHEDIR)/*"
	@echo "chmod -R g+s $(DATADIR)/{media,profiles}"
	@echo "chmod -R g+s $(CACHEDIR)/*"

.PHONY: all clean realclean install
