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

How to cite MMinte
------------------

If you use MMinte for an analysis, please cite this paper:
`MMinte: an application for predicting metabolic interactions among the microbial
species in a community <http://dx.doi.org/doi:10.1186/s12859-016-1230-3>`_

References
----------

The models provided in the mminte/test/data folder are from `Anoxic Conditions Promote
Species-Specific Mutualism between Gut Microbes In Silico <http://dx.doi.org/doi:10.1128/AEM.00101-15>`_.

The 16S sequences present in the database were provided by Maulik Shukla on
the 3rd of November of 2015.