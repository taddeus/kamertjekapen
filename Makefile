.PHONY: all check clean

all: www/style.css www/game.js

www/%.css: %.sass
	sass $< $@

www/%.js: %.coffee
	coffee -o $(@D) $<

check:
	pyflakes *.py
	pep8 *.py

clean:
	rm -f www/*.js www/*.css
