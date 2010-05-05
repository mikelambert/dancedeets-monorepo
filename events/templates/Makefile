
spitfire_compile := spitfire-compile -O3

QUIET := @

SPT_FILES := $(wildcard *.spt)

CTEMPLATES := .

all:
	$(QUIET)$(spitfire_compile) --x-disable-psyco $(SPT_FILES) --output-directory $(CTEMPLATES)
	$(QUIET)touch $(CTEMPLATES)/__init__.py
	$(QUIET)touch $(CTEMPLATES)

