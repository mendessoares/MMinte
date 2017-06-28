
MMinte with your own models
---------------------------

This notebook shows how to perform an interaction analysis using a set
of single species models that you provide. A set of four models for this
tutorial is in the test data included with the mminte package. The
models are a subset of the species analyzed in `Anoxic Conditions
Promote Species-Specific Mutualism between Gut Microbes In
Silico <http://aem.asm.org/content/81/12/4049.full>`__ and include the
following:

-  BT.sbml is a model for Bacteroides thetaiotaomicron
-  FP.sbml is a model for Faecalibacterium prausnitzii
-  HP.sbml is a model for Helicobacter pylori
-  KP.sbml is a model for Klebsiella pneumoniae

Getting started
~~~~~~~~~~~~~~~

Import the mminte package and a few other packages needed for this
tutorial.

.. code:: ipython3

    import mminte
    from os.path import expanduser, join
    from os import makedirs
    import pkg_resources
    import json

The single species models are provided in the test data folder in the
mminte package. Each MMinte widget either creates output files or
returns data that is used as input to the next widget. You need to
select a base folder for storing the output files and separate folders
for the single species and pair model files. Change the value assigned
to ``analysis_folder`` if you want the output files stored somewhere
else.

.. code:: ipython3

    source_folder = pkg_resources.resource_filename('mminte', 'test/data')
    analysis_folder = join(expanduser('~'), 'mminte_interactions')
    pair_model_folder = join(analysis_folder, 'pair_models')

Run the cell below to create the output folders. You only need to run
this cell if the folder does not exist.

.. code:: ipython3

    makedirs(analysis_folder)
    makedirs(pair_model_folder)

When you provide your own models, you can skip the first three widgets
and start the analysis with Widget 4.

Widget 4 - Create two species community models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In Widget 4, you create two species community models from single species
models using the ``create_interaction_models()`` function. The first
input parameter is a list of tuples with two elements, the paths to the
single species model files in each pair. Since the microbial community
is small, select all possible pairs for the analysis. The output is a
list of paths to the six pairs of two species community model files.

.. code:: ipython3

    model_filenames = [join(source_folder, name) for name in ['BT.sbml', 'FP.sbml', 'HP.sbml', 'KP.sbml']]
    pairs = mminte.get_all_pairs(model_filenames)
    pair_model_filenames = mminte.create_interaction_models(pairs, analysis_folder)

For reference, save the list of paths to the two species community
models to a file.

.. code:: ipython3

    with open(join(analysis_folder, 'pair_model_filenames.txt'), 'w') as handle:
        handle.write('\n'.join(pair_model_filenames)+'\n')

Widget 5 - Calculate growth rates and evaluate interactions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In Widget 5, you calculate growth rates and evaluate interactions for
the pairs in the microbial community using the
``calculate_growth_rates()`` function (more details are provided in
"Widget 4" of the tutorial notebook).

The first input parameter is the list of paths to two species community
model files that were created in Widget 4. The second input parameter is
a dictionary that defines the medium (or nutritient conditions) that the
community is growing in. The medium dictionary is keyed by exchange
reaction ID with the uptake rate as the value. The western diet medium
used in the paper is in the test data included with the mminte package.

.. code:: ipython3

    western_diet = json.load(open(pkg_resources.resource_filename('mminte', 'test/data/western.json')))

The output is a data frame with details on the growth rates of the
species in each pair and the type of interaction.

.. code:: ipython3

    growth_rates = mminte.calculate_growth_rates(pair_model_filenames, western_diet)

Each row in the growth\_rates data frame, details the interaction
between a pair in the microbial community and identifies the type of
interaction. This should match paper results

.. code:: ipython3

    growth_rates




.. raw:: html

    <div>
    <style>
        .dataframe thead tr:only-child th {
            text-align: right;
        }
    
        .dataframe thead th {
            text-align: left;
        }
    
        .dataframe tbody tr th {
            vertical-align: top;
        }
    </style>
    <table border="1" class="dataframe">
      <thead>
        <tr style="text-align: right;">
          <th></th>
          <th>A_ID</th>
          <th>B_ID</th>
          <th>TYPE</th>
          <th>TOGETHER</th>
          <th>A_TOGETHER</th>
          <th>B_TOGETHER</th>
          <th>A_ALONE</th>
          <th>B_ALONE</th>
          <th>A_CHANGE</th>
          <th>B_CHANGE</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>0</th>
          <td>BT</td>
          <td>FP</td>
          <td>Parasitism</td>
          <td>0.495075</td>
          <td>0.277463</td>
          <td>0.217612</td>
          <td>0.440738</td>
          <td>0.169338</td>
          <td>-0.370460</td>
          <td>0.285078</td>
        </tr>
        <tr>
          <th>1</th>
          <td>BT</td>
          <td>HP</td>
          <td>Parasitism</td>
          <td>0.500853</td>
          <td>0.036457</td>
          <td>0.464396</td>
          <td>0.440738</td>
          <td>0.197557</td>
          <td>-0.917283</td>
          <td>1.350692</td>
        </tr>
        <tr>
          <th>2</th>
          <td>BT</td>
          <td>KP</td>
          <td>Parasitism</td>
          <td>0.586633</td>
          <td>0.000000</td>
          <td>0.586633</td>
          <td>0.440738</td>
          <td>0.510884</td>
          <td>-1.000000</td>
          <td>0.148269</td>
        </tr>
        <tr>
          <th>3</th>
          <td>FP</td>
          <td>HP</td>
          <td>Commensalism</td>
          <td>0.431667</td>
          <td>0.177563</td>
          <td>0.254104</td>
          <td>0.169338</td>
          <td>0.197557</td>
          <td>0.048574</td>
          <td>0.286228</td>
        </tr>
        <tr>
          <th>4</th>
          <td>FP</td>
          <td>KP</td>
          <td>Amensalism</td>
          <td>0.545572</td>
          <td>0.000000</td>
          <td>0.545572</td>
          <td>0.169338</td>
          <td>0.510884</td>
          <td>-1.000000</td>
          <td>0.067898</td>
        </tr>
        <tr>
          <th>5</th>
          <td>HP</td>
          <td>KP</td>
          <td>Amensalism</td>
          <td>0.540178</td>
          <td>0.000000</td>
          <td>0.540178</td>
          <td>0.197557</td>
          <td>0.510884</td>
          <td>-1.000000</td>
          <td>0.057339</td>
        </tr>
      </tbody>
    </table>
    </div>



For reference, save the growth rates data frame to a file.

.. code:: ipython3

    mminte.write_growth_rates_file(growth_rates, join(analysis_folder, 'growth_rates.csv'))

Widget 6 - Visualize interactions in the community
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In Widget 6, you visualize the interactions between pairs in the
microbial community by creating a graph that represents the interaction
network using make\_graph(). The input is the growth rates data frame
created in Widget 5.

The output is a networkx Graph object where the nodes represent the
different OTUs and the edges represent the interaction between OTUs in a
pair. The color of an edge indicates the kind of interaction predicted
between the OTUs in a pair. A red edge indicates a negative interaction,
a green edge indcates a positive interaction, and a gray edge indicates
no interaction.

.. code:: ipython3

    graph = mminte.make_graph(growth_rates)

You plot the graph using plot\_graph() which opens a new window with the
visualization. The default is a circular layout. If you want a different
layout, you can use any of the plotting functions available in the
networkx package. Note newer versions of matplotlib display deprecation
warnings from networkx drawing functions which can be ignored.

.. code:: ipython3

    %matplotlib
    mminte.plot_graph(graph)


.. parsed-literal::

    Using matplotlib backend: MacOSX


.. parsed-literal::

    /Users/mminte/Envs/mminte/lib/python3.6/site-packages/networkx/drawing/nx_pylab.py:126 [1;31mMatplotlibDeprecationWarning[0m: pyplot.hold is deprecated.
        Future behavior will be consistent with the long-time default:
        plot commands add elements without first clearing the
        Axes and/or Figure.
    /Users/mminte/Envs/mminte/lib/python3.6/site-packages/networkx/drawing/nx_pylab.py:138 [1;31mMatplotlibDeprecationWarning[0m: pyplot.hold is deprecated.
        Future behavior will be consistent with the long-time default:
        plot commands add elements without first clearing the
        Axes and/or Figure.
    /Users/mminte/Envs/mminte/lib/python3.6/site-packages/matplotlib/__init__.py:917 [1;31mUserWarning[0m: axes.hold is deprecated. Please remove it from your matplotlibrc and/or style files.
    /Users/mminte/Envs/mminte/lib/python3.6/site-packages/matplotlib/rcsetup.py:152 [1;31mUserWarning[0m: axes.hold is deprecated, will be removed in 3.0

