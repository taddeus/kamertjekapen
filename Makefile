.PHONY: all clean

all: www/style.css www/game.js

www/%.css: %.sass
	sass $< $@

www/%.js: %.coffee
	coffee -o $(@D) $<

clean:
	rm -f www/*.js www/*.css
