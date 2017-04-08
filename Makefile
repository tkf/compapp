PROJECT = compapp

.PHONY: test clean clean-pycache inject-readme upload

## Testing
test: inject-readme
	tox

clean: clean-pycache
	rm -rf src/*.egg-info .tox MANIFEST

clean-pycache:
	find src -name __pycache__ -o -name '*.pyc' -print0 \
		| xargs --null rm -rf

## Update files using inject-readme.py
inject-readme: src/$(PROJECT)/__init__.py
src/$(PROJECT)/__init__.py: README.rst
	sed '1,/^"""$$/d' $@ > $@.tail
	rm $@
	echo '"""' >> $@
	cat README.rst >> $@
	echo '"""' >> $@
	cat $@.tail >> $@
	rm $@.tail
# Note that sed '1,/^"""$/d' prints the lines after the SECOND """
# because the first """ appears at the first line.

## Upload to PyPI
upload: inject-readme
	python setup.py register sdist upload
