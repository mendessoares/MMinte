Microbial Metabolic Interactions
================================

**MMinte** (pronounced /‘minti/) is a set of widgets that allows you to explore
the pairwise interactions (positive or negative) that occur in a microbial
community. From an association network and 16S rDNA sequence data, **MMinte**
identifies corresponding genomes, reconstructs metabolic models, estimates
growth under specific metabolic conditions, analyzes pairwise interactions,
assigns interaction types to network links, and generates the corresponding
network of interactions.

Installation
------------

Use pip to install **MMinte** from `PyPI <https://pypi.python.org/pypi/mminte>`_
(we recommend doing this inside a `virtual environment
<http://docs.python-guide.org/en/latest/dev/virtualenvs/>`_)::

    pip install mminte

Note that **MMinte** requires cobrapy 0.5.11. Python versions 2.7.11+, Python 3.5+,
or Python 3.6+ are recommended.

Virtual environment installation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Here are step-by-step instructions for installing **MMinte** in a virtual environment.

1. If virtualenvwrapper is not installed, `follow the directions <https://virtualenvwrapper.readthedocs.io/en/stable/>`_
   to install virtualenvwrapper. You should also `update your shell startup file
   <http://virtualenvwrapper.readthedocs.io/en/stable/install.html#shell-startup-file>`_.

   Note on macOS El Capitan there is a known problem with the virtualenvwrapper
   dependency on the six package. For a work-around use this command:

    $ pip install virtualenvwrapper --upgrade --ignore-installed six

2. Create a virtualenv for **MMinte** with these commands::

    $ mkvirtualenv mminte

   Use the ``--python`` option to select a specific version of Python for the
   virtualenv. For example, ``python=python3`` to select the current python3
   installed on the system.

   Note on macOS, matplotlib requires Python be installed as a framework but
   virtualenv creates a non-framework build of Python. See the
   `matplotlib FAQ <http://matplotlib.org/1.5.3/faq/virtualenv_faq.html>`_
   for details on a workaround.

3. Upgrade pip and setuptools to the latest versions with this command::

    (mminte)$ pip install --upgrade pip setuptools

4. Install the base **MMinte** package with this command::

    (mminte)$ pip install mminte

5. If you want to verify the installation with the included tests, install the
   test dependencies and run the tests with these commands::

    (mminte)$ pip install mminte[test]
    (mminte)$ pytest mminte -v

6. When you are done using **MMinte**, you can switch back to the system-installed
   version of Python with this command::

    (mminte)$ deactivate

   Start the **MMinte** virtualenv again with this command::

    (mminte)$ workon mminte

How to run an analysis with MMinte
----------------------------------

There are two ways to run an analysis with **MMinte**.

In a notebook
^^^^^^^^^^^^^

A tutorial of how to use **MMinte** is provided in a Jupyter notebook. Here's how to
start Jupyter and run the notebook from the virtual environment.

1. Install Jupyter with this command::

    (mminte)$ pip install jupyter

2. Install a kernel that uses the virtualenv installation with this command::

    (mminte)$ ipython kernel install --name "MMinte" --user

3. Start the Jupyter notebook server with this command::

    (mminte)$ jupyter notebook

   Jupyter opens a web page in your default browser with a file browser.

4. Navigate to the folder where **MMinte** is installed (use `pip show mminte` to
   find the folder) and in the "notebooks" folder click on the "tutorial.ipynb"
   notebook.

5. After the notebook opens, from the "Kernel" menu, select "Change kernel" and
   click on "MMinte".

6. Now you can run the cells in the notebook.

In a web browser
^^^^^^^^^^^^^^^^

**MMinte** includes a web site that allows you to run each widget from a web browser.
The web site runs on your local system and requires that you use a folder on the
local system for storing the results of the analysis. Here's how to start the web site:

1. Install the additional packages needed for the web site interface with this command::

    (mminte)$ pip install mminte[site]

2. Start the web server with this command::

    (mminte)$ launchMMinte
    Logging to "/var/folders/pz/r04ddhtx6vgb48tg0dn5cys8vz00jn/T" folder
    [14/Apr/2017:14:25:04] ENGINE Listening for SIGHUP.
    [14/Apr/2017:14:25:04] ENGINE Listening for SIGTERM.
    [14/Apr/2017:14:25:04] ENGINE Listening for SIGUSR1.
    [14/Apr/2017:14:25:04] ENGINE Bus STARTING
    CherryPy Checker:
    The Application mounted at '' has an empty config.

    [14/Apr/2017:14:25:04] ENGINE Started monitor thread 'Autoreloader'.
    [14/Apr/2017:14:25:04] ENGINE Started monitor thread '_TimeoutMonitor'.
    [14/Apr/2017:14:25:04] ENGINE Serving on http://127.0.0.1:8080
    [14/Apr/2017:14:25:04] ENGINE Bus STARTED

   When you see the ``ENGINE Bus STARTED`` message, the web server is ready.

3. If another service is using port 8080, you can start the web server on a different
   port with this command::

    (mminte)$ launchMMinte --port 8099

4. Open a web browser and go to ``http://localhost:8080`` (change the port number
   if you started the web server on a different port) and follow the directions to
   run your analysis.

Release Notes
-------------

Version 1.0.3 (June 27, 2017)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Added save_model_to_file() function
* Added apply_medium() function to default import

Version 1.0.2 (May 18, 2017)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Updated handling of objectives for compatibility with cobra 0.6
* Fixed display of interaction network visualization when using different analysis
  folder in web site interface

Version 1.0.1 (May 5, 2017)
^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Updated directions for virtual environment installation
* Updated version dependency for mackinac
* Fixed reading files with different newline characters
* Added notebooks to package distribution and updated directions

Version 1.0 (April 17, 2017)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Refactor of `original MMinte <https://github.com/mendessoares/MMinte>`_ with

* a simpler interface for functions,
* multiprocessing support for creating interaction models and calculating growth rates,
* updated web site that uses new version of DataSpyre,
* documentation in Jupyter notebooks,
* a test suite,
* reorganized repository to enable installation with pip.

How to cite MMinte
------------------

If you use **MMinte** for an analysis, please cite this paper:
`MMinte: an application for predicting metabolic interactions among the microbial
species in a community <http://dx.doi.org/doi:10.1186/s12859-016-1230-3>`_

Additional References
---------------------

1. The models provided in the mminte/test/data folder are from `Anoxic Conditions Promote
   Species-Specific Mutualism between Gut Microbes In Silico <http://dx.doi.org/doi:10.1128/AEM.00101-15>`_.

2. The 16S sequences included in the database were provided by Maulik Shukla on
   the 3rd of November of 2015.