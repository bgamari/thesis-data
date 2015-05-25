overview.html : overview.mkd style.css filter.hs
	pandoc --to=html5 --standalone --css style.css $< -o $@ --filter ./filter.hs
