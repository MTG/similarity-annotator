.PHONY: deploy all
deploy:
	mkdir -p /static
	mkdir -p /static/js
	cp node_modules/peaks.js/peaks.js /static/js
	cp -r node_modules/bootstrap/dist/* /static

all: deploy
