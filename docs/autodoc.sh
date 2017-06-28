rm mminte*.rst
sphinx-apidoc -o . ../mminte ../mminte/site ../mminte/test
rm modules.rst
jupyter nbconvert --to=rst ../mminte/notebooks/*.ipynb
mv ../mminte/notebooks/*.rst .