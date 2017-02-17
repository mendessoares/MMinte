Microbial Metabolic Interactions
================================

**MMinte** (pronounced /‘minti/) is an integrated pipeline that allows users
to explore the pairwise interactions (positive or negative) that occur in a
microbial network. From an association network and 16S rDNA sequence data,
**MMinte** identifies corresponding genomes, reconstructs metabolic models,
estimates growth under specific metabolic conditions, analyzes pairwise
interactions, assigns interaction types to network links, and generates the
corresponding network of interactions.

Installation
------------

**Coming soon ...**

Use pip to install mminte-mp from `PyPI <https://pypi.python.org/pypi/mminte-mp>`_
(we recommend doing this inside a `virtual environment
<http://docs.python-guide.org/en/latest/dev/virtualenvs/>`_)::

    pip install mminte

mminte requires the cobra, pandas, and six packages. Using SBML models requires
the python-libsbml and lxml packages.

