
spitfire_compile := spitfire-compile -O3

QUIET := @

SPT_FILES := $(wildcard *.spt)

all:
	$(QUIET)$(spitfire_compile) --x-disable-psyco $(SPT_FILES)
	$(QUIET)touch ./__init__.py
	$(QUIET)touch .

