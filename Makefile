compile-jsx:
	jsx --no-cache-dir tableau/static/jsx/src tableau/static/jsx/build

copy-jsx: compile-jsx
	cp tableau/static/jsx/build/*js tableau/templates