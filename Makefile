PIP3 ?= pip3
PYTHON3 ?= python3

examples = \
    erts \
    kernel \
    stdlib \
    $(NULL)

html_stamps = \
    _build/test-doc-stamp  \
    _build/doc-stamp \
    _build/readme-stamp \
    _build/examples-stamp \
    $(NULL)

.PHONY: all
DEFAULT_TARGET ?=
all: $(DEFAULT_TARGET)

.PHONY: check
CHECK_TARGET ?= html-all
check: $(CHECK_TARGET)

.PHONY: html-all
html-all: $(html_stamps)

.PHONY: clean
clean:
	rm -rf build
	rm -rf _build
	rm -rf examples/*/_build
	rm -rf test/_build

.PHONY: dist
dist:
	$(PYTHON3) -m build

.PHONY: dist.deprecated
dist.deprecated:
	$(PIP3) install -U setuptools wheel
	$(PYTHON3) setup.py release sdist bdist_wheel

#--[test-doc]----
_build/test-doc-stamp: | _build/html
	$(MAKE) -C test html
	ln -sf ../../test/_build/html _build/html/test
	touch $@

#--[doc]----
_build/doc-stamp: doc/index.rst doc/reference.rst doc/readme.rst README.rst
_build/doc-stamp: | _build/html
	$(MAKE) -C doc html
	ln -sf ../../doc/_build/html _build/html/doc
	touch $@

#--[readme]----
_build/readme-stamp: _build/readme/conf.py _build/readme/index.rst _build/readme/Makefile | _build/html
	$(MAKE) -C _build/readme html
	ln -sf ../readme/_build/html _build/html/readme
	touch $@

_build/readme/Makefile: test/Makefile | _build/readme
	cp $< $@.tmp && mv $@.tmp $@

_build/readme/conf.py: test/conf.py | _build/readme
	cp $< $@.tmp && mv $@.tmp $@

_build/readme/index.rst: README.rst | _build/readme
	cp $< $@.tmp && mv $@.tmp $@

#--[examples]----
_build/examples-stamp: $(examples:%=_build/example-%-stamp)
_build/example-%-stamp: dir=$(@:_build/example-%-stamp=%)
_build/example-%-stamp: | _build/html
	$(MAKE) -C examples/$(dir) html
	ln -sf ../../examples/$(dir)/_build/html _build/html/$(dir)
	touch $@

_build/example-erts-stamp: examples/erts/erlang.rst
_build/example-erts-stamp: examples/erts/index.rst
_build/example-kernel-stamp: examples/kernel/file.rst
_build/example-kernel-stamp: examples/kernel/gen_tcp.rst
_build/example-kernel-stamp: examples/kernel/index.rst
_build/example-kernel-stamp: examples/kernel/inet.rst
_build/example-stdlib-stamp: examples/stdlib/index.rst
_build/example-stdlib-stamp: examples/stdlib/lists.rst
_build/example-stdlib-stamp: examples/stdlib/unicode.rst

#--[dirs]----
_build:
	mkdir $@
_build/readme: | _build
	mkdir $@
_build/html: | _build
	mkdir $@
