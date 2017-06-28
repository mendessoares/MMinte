
MMinte pipeline tutorial
------------------------

**MMinte** (pronounced /‘minti/) is a set of widgets that allows you to
explore the pairwise interactions (positive or negative) that occur in a
microbial community. From an association network and 16S rDNA sequence
data, **MMinte** identifies corresponding genomes, reconstructs
metabolic models, estimates growth under specific metabolic conditions,
analyzes pairwise interactions, assigns interaction types to network
links, and generates the corresponding network of interactions.

This tutorial shows how to run all six widgets in an integrated pipeline
from start to finish. See `MMinte with your own
models <interactions.ipynb>`__ for a tutorial on how to run specific
steps in the pipeline when you already have metabolic models for the
organisms in a microbial community.

Getting started
~~~~~~~~~~~~~~~

**MMinte** can reconstruct ModelSEED models for the species in the
microbial community using Widget 3. The `ModelSEED
service <http://modelseed.org>`__ uses genomes available in the
`Pathosystems Resource Integration
Center <https://www.patricbrc.org/portal/portal/patric/Home>`__ (PATRIC)
and requires you to authenticate as a `registered PATRIC
user <http://enews.patricbrc.org/faqs/workspace-faqs/registration-faqs/>`__.
If needed, complete a `new user
registration <https://user.patricbrc.org/register/>`__. Before you use
Widget 3 you must get an authentication token. The
`Mackinac <https://github.com/mmundy42/mackinac>`__ ``get_token()``
function stores the authentication token in the ``.patric_config`` file
in your home directory. You can use the token until it expires.

In the cell below, change ``username`` to your PATRIC username and enter
your password when prompted. The returned user ID identifies your
ModelSEED workspace.

.. code:: ipython3

    from mackinac import get_token
    get_token('username')


.. parsed-literal::

    patric password: ········




.. parsed-literal::

    'username@patricbrc.org'



Now import the mminte package and a few other packages needed for this
tutorial.

.. code:: ipython3

    import mminte
    from os.path import expanduser, join
    from os import makedirs
    import pkg_resources

Each **MMinte** widget either creates output files or returns data that
is used as input to the next widget. You need to select a base folder
for storing the output files and separate folders for the single species
and pair model files. Since there can be a large number of model files,
it helps to store them in a separate folders. Change the value assigned
to ``analysis_folder`` if you want the output files stored somewhere
else.

.. code:: ipython3

    analysis_folder = join(expanduser('~'), 'mminte_tutorial')
    single_model_folder = join(analysis_folder, 'single_models')
    pair_model_folder = join(analysis_folder, 'pair_models')

Run the cell below to create the folders. You only need to run this cell
if the folders do not exist.

.. code:: ipython3

    makedirs(analysis_folder)
    makedirs(single_model_folder)
    makedirs(pair_model_folder)

Widget 1 - Get sequences for representative OTUs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In Widget 1, you get the 16S rDNA sequences for the representative OTUs
in the microbial community using the ``get_unique_otu_sequences()``
function. The first input parameter is a list of tuples that has three
elements: (1) first OTU number, (2) second OTU number, and (3)
correlation value between -1 and 1. You need to provide this data based
on your own analysis of the microbial community.

A correlation file for this tutorial is in the test data included with
the mminte package. Each line of the correlation file has three columns:
(1) first OTU number, (2) second OTU number, and (3) correlation value.
For example:

::

    18  310 0.98
    18  401 1
    18  405 0.92
    37  72  0.96    
    37  74  1
    37  632 -0.2

Each column in the correlation file is separated by a tab and the first
line of the line is a header that is ignored. The correlation file is
used again in Widget 6 to visualize the results.

Change the value assigned to ``correlation_filename`` if you want to use
your own correlation file.

.. code:: ipython3

    correlation_filename = pkg_resources.resource_filename('mminte', 'test/data/correlation.txt')
    correlations = mminte.read_correlation_file(correlation_filename)

The second input parameter is the path to a fasta file that has the 16S
rDNA sequences for all of the OTUs in the microbial community. The
record ID in each fasta record must be an OTU number. All of the OTUs in
the correlation file must have a record in the fasta file.

Typically you get the fasta file as output from 16S rDNA sequencing of
the microbial community. A fasta file for this tutorial is in the test
data included with the mminte package. The data in the fasta file comes
from the Human Microbiome Project. Change the value assigned to
``all_otus_filename`` if you want to use your own sequence file.

.. code:: ipython3

    all_otus_filename = pkg_resources.resource_filename('mminte', 'test/data/all_otus.fasta')

The third input parameter is the path to a fasta file where the 16S rDNA
sequences for the unique representative OTUs are stored.

.. code:: ipython3

    unique_otus_filename = join(analysis_folder, 'unique_otus.fasta')

The output is the number of unique OTUs that are found in the input
files.

.. code:: ipython3

    mminte.get_unique_otu_sequences(correlations, all_otus_filename, unique_otus_filename)




.. parsed-literal::

    18



Widget 2 - Search for closest matching bacterial species
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In Widget 2, you use the unique representative OTU sequences to find the
closest matching bacterial species with a whole genome sequence by
running blast using the ``search()`` function. The first input parameter
is the path to a fasta file with the 16S rDNA sequences for the unique
OTUs that was created in Widget 1. The second input parameter is the
path to the blast output file. *Talk about how database was generated*

The two outputs are (1) a list of the unique NCBI genome IDs and (2) a
data frame with the percent similarity between each representative OTUs
and the closest match, identified by the NCBI genome ID.

.. code:: ipython3

    genome_ids, similarity = mminte.search(unique_otus_filename, join(analysis_folder, 'blast.txt'))

Each row in the ``similarity`` data frame has three columns: (1) OTU ID,
(2) NCBI genome ID, and (3) percent similarity of the organism
represented by the OTU number to the organism with the NCBI genome ID.
For example:

.. code:: ipython3

    similarity[0:10]




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
          <th>OTU_ID</th>
          <th>GENOME_ID</th>
          <th>SIMILARITY</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>0</th>
          <td>18</td>
          <td>657315.3</td>
          <td>100.00</td>
        </tr>
        <tr>
          <th>1</th>
          <td>37</td>
          <td>484018.6</td>
          <td>98.33</td>
        </tr>
        <tr>
          <th>2</th>
          <td>72</td>
          <td>1235835.3</td>
          <td>25.00</td>
        </tr>
        <tr>
          <th>3</th>
          <td>74</td>
          <td>742823.3</td>
          <td>100.00</td>
        </tr>
        <tr>
          <th>4</th>
          <td>109</td>
          <td>1414720.3</td>
          <td>25.22</td>
        </tr>
        <tr>
          <th>5</th>
          <td>112</td>
          <td>1156417.3</td>
          <td>90.64</td>
        </tr>
        <tr>
          <th>6</th>
          <td>150</td>
          <td>180332.3</td>
          <td>0.00</td>
        </tr>
        <tr>
          <th>7</th>
          <td>221</td>
          <td>717962.3</td>
          <td>99.16</td>
        </tr>
        <tr>
          <th>8</th>
          <td>243</td>
          <td>1297617.3</td>
          <td>91.85</td>
        </tr>
        <tr>
          <th>9</th>
          <td>253</td>
          <td>1367212.3</td>
          <td>97.24</td>
        </tr>
      </tbody>
    </table>
    </div>



For reference, save the genome IDs and similarity data frame to files.

.. code:: ipython3

    with open(join(analysis_folder, 'genome_ids.txt'), 'w') as handle:
        handle.write('\n'.join(genome_ids)+'\n')
    mminte.write_similarity_file(similarity, join(analysis_folder, 'similarity.csv'))

Widget 3 - Reconstruct and download metabolic models from ModelSEED
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In Widget 3, you reconstruct and gap fill metabolic models for the
unique species in the microbial community with the `ModelSEED
service <http://modelseed.org>`__ using the ``create_species_models()``
function. The first input parameter is the list of genome IDs that was
created in Widget 2. The second input parameter is the path to a folder
for storing the single species model files (created in "Getting
Started").

The output is a list of paths to the downloaded single species model
files. The ``create_species_models()`` function can run for a long time
if all of the models need to be reconstructed and gap filled. By
default, ``create_species_models()`` uses a previously downloaded model
or a previously reconstructed model available in your ModelSEED
workspace. You can force the models to be reconstructed using the
``replace=True`` parameter.

The output is a list of paths to the downloaded single species model
files.

.. code:: ipython3

    single_model_filenames = mminte.create_species_models(genome_ids, single_model_folder)

For reference, save the list of paths to single species models to a
file.

.. code:: ipython3

    with open(join(analysis_folder, 'single_model_filenames.txt'), 'w') as handle:
        handle.write('\n'.join(single_model_filenames)+'\n')

Widget 4 - Create two species community models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In Widget 4, you create two species community models from single species
models using the ``create_interaction_models()`` function. The first
input parameter is a list of tuples with two elements, the paths to the
single species model files in each pair. You can use all possible pairs
from the list of single species models created in Widget 3 as shown in
the cell below or select specific pairs by building the input list
yourself.

.. code:: ipython3

    pairs = mminte.get_all_pairs(single_model_filenames)
    pairs[0]




.. parsed-literal::

    ('/Users/mminte/mminte_tutorial/single_models/557855.3.json',
     '/Users/mminte/mminte_tutorial/single_models/1414720.3.json')



The second input parameter is the path to a folder for storing the two
species community model files (created in "Getting Started").

The output is a list of paths to the two species community model files.

.. code:: ipython3

    pair_model_filenames = mminte.create_interaction_models(pairs, pair_model_folder)

For reference, save the list of paths to the two species community
models to a file.

.. code:: ipython3

    with open(join(analysis_folder, 'pair_model_filenames.txt'), 'w') as handle:
        handle.write('\n'.join(pair_model_filenames)+'\n')

Widget 5 - Calculate growth rates and evaluate interactions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In Widget 5, you calculate growth rates and evaluate interactions for
the pairs in the microbial community using the
``calculate_growth_rates()`` function. To determine how the presence of
one species in the community affects the growth of the other species,
the two species community model is optimized for growth with the two
species together and with each species alone under specific nutritient
conditions. The type of interaction is set based on the outcomes
identified in Table 1 of `Anoxic Conditions Promote Species-Specific
Mutualism between Gut Microbes In
Silico <http://aem.asm.org/content/81/12/4049.full>`__. What happens
between two species may be broadly divided into positive, negative, or
no interaction.

The first input parameter is the list of paths to two species community
model files that were created in Widget 4.

The second input parameter is a dictionary that defines the medium (or
nutritient conditions) that the community is growing in. The medium
dictionary is keyed by exchange reaction ID with the uptake rate as the
value. A complete medium for the ModelSEED models used in this tutorial
is in the test data included with the mminte package.

.. code:: ipython3

    complete_diet = mminte.read_diet_file(pkg_resources.resource_filename('mminte', 'test/data/ms_complete100.txt'))

The output is a data frame with details on the growth rates of the
species in each pair and the type of interaction.

.. code:: ipython3

    growth_rates = mminte.calculate_growth_rates(pair_model_filenames, complete_diet)

Each row in the ``growth_rates`` data frame, details the interaction
between a pair in the microbial community and identifies the type of
interaction.

.. code:: ipython3

    growth_rates[0:10]




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
          <td>557855.3</td>
          <td>1414720.3</td>
          <td>Mutualism</td>
          <td>146.980271</td>
          <td>133.190104</td>
          <td>13.790167</td>
          <td>119.938824</td>
          <td>5.916418</td>
          <td>0.110484</td>
          <td>1.330830</td>
        </tr>
        <tr>
          <th>1</th>
          <td>557855.3</td>
          <td>29354.3</td>
          <td>Parasitism</td>
          <td>163.340523</td>
          <td>151.715807</td>
          <td>11.624716</td>
          <td>119.938824</td>
          <td>25.000801</td>
          <td>0.264943</td>
          <td>-0.535026</td>
        </tr>
        <tr>
          <th>2</th>
          <td>557855.3</td>
          <td>1165092.3</td>
          <td>Parasitism</td>
          <td>150.759397</td>
          <td>145.183478</td>
          <td>5.575919</td>
          <td>119.938824</td>
          <td>22.060714</td>
          <td>0.210479</td>
          <td>-0.747247</td>
        </tr>
        <tr>
          <th>3</th>
          <td>557855.3</td>
          <td>1156417.3</td>
          <td>Amensalism</td>
          <td>125.207214</td>
          <td>124.183373</td>
          <td>1.023841</td>
          <td>119.938824</td>
          <td>9.510915</td>
          <td>0.035389</td>
          <td>-0.892351</td>
        </tr>
        <tr>
          <th>4</th>
          <td>557855.3</td>
          <td>1235835.3</td>
          <td>Amensalism</td>
          <td>119.938824</td>
          <td>119.938824</td>
          <td>0.000000</td>
          <td>119.938824</td>
          <td>2.145181</td>
          <td>0.000000</td>
          <td>-1.000000</td>
        </tr>
        <tr>
          <th>5</th>
          <td>557855.3</td>
          <td>1469948.3</td>
          <td>Parasitism</td>
          <td>136.863863</td>
          <td>136.863863</td>
          <td>0.000000</td>
          <td>119.938824</td>
          <td>6.230712</td>
          <td>0.141114</td>
          <td>-1.000000</td>
        </tr>
        <tr>
          <th>6</th>
          <td>557855.3</td>
          <td>1297617.3</td>
          <td>Amensalism</td>
          <td>129.488623</td>
          <td>129.488623</td>
          <td>0.000000</td>
          <td>119.938824</td>
          <td>8.269206</td>
          <td>0.079622</td>
          <td>-1.000000</td>
        </tr>
        <tr>
          <th>7</th>
          <td>557855.3</td>
          <td>742726.3</td>
          <td>Amensalism</td>
          <td>119.938824</td>
          <td>119.938824</td>
          <td>0.000000</td>
          <td>119.938824</td>
          <td>0.000000</td>
          <td>0.000000</td>
          <td>-1.000000</td>
        </tr>
        <tr>
          <th>8</th>
          <td>557855.3</td>
          <td>742823.3</td>
          <td>Parasitism</td>
          <td>134.965308</td>
          <td>134.965308</td>
          <td>0.000000</td>
          <td>119.938824</td>
          <td>0.000000</td>
          <td>0.125285</td>
          <td>-1.000000</td>
        </tr>
        <tr>
          <th>9</th>
          <td>557855.3</td>
          <td>1367212.3</td>
          <td>Amensalism</td>
          <td>125.359516</td>
          <td>125.359516</td>
          <td>0.000000</td>
          <td>119.938824</td>
          <td>2.389163</td>
          <td>0.045195</td>
          <td>-1.000000</td>
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
network using ``make_graph()``.

The first input is the growth rates data frame created in Widget 5. The
second input parameter is the similarity data frame created in Widget 2.
The third input parameter is the correlations between OTUs used as input
in Widget 1.

The output is a networkx Graph object where the nodes represent the
different OTUs and the edges represent the interaction between OTUs in a
pair. The shading of a node indicates how close the sequence of the OTU
is to the sequence of the genome. The darker the node, the higher the
similarity. The color of an edge indicates the kind of interaction
predicted between the OTUs in a pair. A red edge indicates a negative
interaction, a green edge indcates a positive interaction, and a gray
edge indicates no interaction. The thickness of an edge indicates the
strength of the correlation between the OTUs in a pair. The thicker the
edge, the higher the correlation between the OTUs.

.. code:: ipython3

    graph = mminte.make_graph(growth_rates, similarity, correlations)

You plot the graph using ``plot_graph()`` which opens a new window with
the visualization. The default is a circular layout. If you want a
different layout, you can use any of the plotting functions available in
the networkx package. Note newer versions of matplotlib display
deprecation warnings from networkx drawing functions which can be
ignored.

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

