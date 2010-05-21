
spitfire_compile := spitfire-compile -O3

QUIET := @

SPT_FILES := $(wildcard *.spt)

CTEMPLATES := ../compiled_templates/

all:
	$(QUIET)mkdir -p $(CTEMPLATES)
	$(QUIET)$(spitfire_compile) --x-disable-psyco $(SPT_FILES) --output-directory $(CTEMPLATES)
	$(QUIET)touch $(CTEMPLATES)/__init__.py
	$(QUIET)touch $(CTEMPLATES)

