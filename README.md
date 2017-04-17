# Announcement 04/17/2017
## MMinte1.0 is out!!!
You can dowload it from pypi: https://pypi.python.org/pypi/mminte/1.0.0

Or, you can go to https://github.com/mmundy42/MMinte   and get it from there!

Let us know how it works for you! And please continue citing the original paper!

-H.

# Announcement 03/07/2017
## An updated version of MMinte will be coming soon.
The features include:

-Download through pypi.

-Easy installation across systems.

-MUUUUUUUUUCH faster!

-Jupyter notebooks allowing you to easily explore your data from the command line.

Come back soon.

H.


# Announcement 01/06/2017
## We're back on! - H.


# Announcement 12/29/2016

##The ModelSEED server is not responding to requests from MMinte. We are working to fix this issue and hope to have everything up and running again next week. Thanks - H.

##MMinte version 1.3 08/06/2016

####CONTACT INFORMATION
Project folder: www.github.com/mendessoares/MMinte <br>
E-mail: microbialmetabolicinteractions@gmail.com 

####DESCRIPTION

__MMinte__ (pronounced /‘minti/) is an integrated pipeline that allows users to explore the pairwise interactions (positive or negative) that occur in a microbial network. From an association network and 16S rDNA sequence data, __MMinte__ identifies corresponding genomes, reconstructs metabolic models, estimates growth under specific metabolic conditions, analyzes pairwise interactions, assigns interaction types to network links, and generates the corresponding network of interactions. Our application is composed of seven widgets that run sequentially, and each widget may also be run as independent modules. 


__MMinte__ is composed of 7 widgets that may be run sequentially or individually:

* _Widget 1_: Using information about pairs of operational taxonomic units (OTUs) that are associated to some degree and a list of 16S rDNA sequences for the OTUs in a particular community, a file is created containing only the sequences for representative OTUs significant to the analyses.
* _Widget 2_: The representative OTUs are identified and assigned a genome ID using BLAST and a local database containing the 16S rDNA sequences of species with whole genome sequences.
* _Widget 3_:  Metabolic models for each genome ID are reconstructed and gap-filled using ModelSEED and downloaded to the user’s local machine.
* _Widget 4_:  Metabolic models of 2-species communities are created using COBRA Tools for the python computational framework (COBRApy). 
* _Widget 5_: Under defined metabolic conditions, the growth rates of each species in isolation and when in the presence of another species in the community are estimated.
* _Widget 6_: The kinds of interactions occurring between the pairs of species on the metabolic conditions defined Widget 5 are predicted. The interactions are either positive (commensalism, mutualism) or negative (parasitism, amensalism, competition). The interactions are determined by their effect on the predicted growth rates of the species when compared to growth in isolation. When the effect is over 10%, we consider that an interaction is occurring. The direction is considered negative of positive to the focal species depending on whether the species is predicted to grow slower or faster in a community, respectively. Positive interactions are the ones where at least one species benefits from the interactions and no species suffers from it (mutualism: + +; commensalism: + 0). Negative interaction are interactions where at least one species suffers negative from the interactions (parasitism: + -; amensalsm: - 0; competition: - -). Neutralism represents no interactions between the species.
* _Widget 7_: A network is plotted with D3.js using the initial information of associations between the pairs of OTUs provided by the user, and the kinds of interactions predicted to be occurring.



####GENERAL USAGE NOTES
- __MMinte__ has only been tested in Linux systems. We include an installation files for Windows machines but do not guarantee it will work.

- Part of __MMinte__ (Widget 3) interacts with ModelSEED. We will try to maintain __MMinte__ updated in github to reflect the changes ModelSEED is going through, so make sure you check back every once in a while.

- To start __MMinte__, you need to use the command-line. Everything else can be done through drag and drop of files and point-and-click of tasks on a web browser. 

- Make sure you go over the instructions for installation (below) and usage (below and tutorials).

- If you have any questions at all, just contact us. We're happy to help you out with your analysis even if it deviates a little from what __MMinte__ currently does. For instance, you can use streamline the code to recursively go through a variety of metabolic conditions.

- For example and testing purposes, each widget can be run with example files (stored in MMinte/supportFiles/exampleRun/userFiles/). Jsut make sure you type '<b>Yes</b>' in the top box in each Widget.


####INSTALLATION

#####What do I need to have installed in my machine before setting up MMinte?

* __Python 2.7__
	* __MMinte__ was only tested in Python 2.7. I'm not saying it won't work on Python 3, but you have to try at your own risk. To see which version of Python you have on your machine, open the terminal window and type ``python --version ``. You can find instructions on how to download and install Python on your machine from https://www.python.org/downloads/ .
	
* __pip__
	* pip is awesome. You can easily install all __MMinte__'s requirements by calling the install command of pip. You can find instructions on how to download and install pip on your machine from http://pip.readthedocs.org/en/stable/ .

If you have neither __Python 2.7__ or __pip__ installed you can either install them separately as suggested above or you can use home-brew from the terminal in __Mac__ (if you don't have homebrew installed, follow the instructions on the webpage http://brew.sh/ -it's really just one line of code) and type ``brew install pip`` . You can type ``apt-get install python-pip`` if you are using __Linux__ instead.

* __virtualenv__ - To make sure the versions of all of __MMinte__'s dependencies are correct and no conflicts occur, we suggest you run __MMinte__ in a virtual environment. __virtualenv__ is pretty neat and, from the site of the developers on https://virtualenv.readthedocs.org/en/latest/# , "is a tool to create isolated Python environments". You can find the instructions for downloading and installing __virtualenv__ on that page. In summary, you can just type ``pip install virtualenv`` (see how __pip__ is so handy?)



#####How do I setup MMinte?
1. Download the __MMinte__ package. To do this go to http://github.com/mendessoares/MMinte and click on Download ZIP button on the right side of the screen. This will (likely) download the ZIP file to your Downloads folder.
2. Your Downloads folder now has a MMinte_package.zip file. You can uncompress this file by double clicking the file. This will create the folder MMinte_package on your downloads folder. Move this folder to where you would like to keep it permanently. I suggest you move it to your Documents folder. You can do this by dragging the folder to Documents folder, or through command line. Here's how to do the latest. Open terminal, then type: ``cd ~/Downloads/MMinte-master`` and press Enter. Then type ``mv MMinte/ ~/Documents/`` and press Enter. The MMinte_package folder should now be on your Documents folder.
2. Use the terminal on your machine to go to the MMinte_package folder by typing ``cd ~/Documents/MMinte/``
3. Create a virtual environment by typing ``virtualenv env``.
4. This will create a folder in __MMinte__ called env. This is where all the packages and modules you need for doing all the analysis will be stored. This avoids potential conflicts between the versions of packages and modules needed for __MMinte__ and any you may have in your system. You can see this folder listed if you type ``ls`` on the terminal
5. Enter your virtual environment by typing ``source env/bin/activate`` . This command assumes you are right outside your env folder. If you are not sure where you are, type ``cd ~/Documents/MMinte/`` , press enter, and try entering your virtual environment again.
6. We will now install all the dependencies required for __MMinte__ to run. If you are working on a MacOS system, type ``bash installation/install-requiredPKGMacOS.sh`` . If you are working on a Linux system, type ``bash installation/install-requiredPKGLinux.sh`` . Wait for everything to get installed. The Python module __libsbml__ takes quite a while to get installed, so the whole process takes around 10 minutes on an average speed internet connection. If no warnings show up on the terminal window when the prompt in the terminal (``$``) shows up, then all was successfully installed. If you get an error message from BioPython saying that numpy is not installed, don't worry. numpy is not needed for __MMinte__ to work.
7. You are now ready to run __MMinte__ from your virtual environment.
8. If you don't want to run __MMinte__ at this point, you can deactivate your virtual environment by typing ``deactivate`` and closing the terminal. If you want to go ahead and run __MMinte__, go to the section __How do I run MMinte__  and start from step 4 in the section title __How do I run MMinte?__.


####FILE LIST (essential)

* MMinte/installation/install-requiredPKGLinux.sh
* MMinte/installation/install-requiredPKGMacOS.sh
* MMinte/installation/install-requiredPKGWindows.sh<br>
(installation files will create ncbi-blast-2.2.22+ folder)
* MMinte/site/static/images/3485812-14.jpg
* MMinte/site/static/images/flow.jpg
* MMinte/site/static/d3.v3.min.js
* MMinte/site/static/index.html
* MMinte/site/static/launchMMinte.py
* MMinte/site/static/MMinteW1.py
* MMinte/site/static/MMinteW2.py
* MMinte/site/static/MMinteW3.py
* MMinte/site/static/MMinteW4.py
* MMinte/site/static/MMinteW5.py
* MMinte/site/static/MMinteW6.py
* MMinte/site/static/MMinteW7.py
* MMinte/site/static/MMinterunAll.py
* MMinte/site/static/widget1.py
* MMinte/site/static/widget2.py
* MMinte/site/static/widget3.py
* MMinte/site/static/widget4.py
* MMinte/site/static/widget5.py
* MMinte/site/static/widget6.py
* MMinte/site/static/widget7.py
* MMinte/supportFiles/Diets/Diets.txt
* MMinte/supportFiles/db/16Sdb.nhr
* MMinte/supportFiles/db/16Sdb.nin
* MMinte/supportFiles/db/16Sdb.nsi
* MMinte/supportFiles/db/16Sdb.nsq
* MMinte/supportFiles/exampleRun/userFiles/corrs.txt
* MMinte/supportFiles/exampleRun/userFiles/otus.fasta


####PYTHON MODULES INSTALLED DURING SETUP

Most of us are scientists with little or no formal training in software package development. The only reason we were able to put __MMinte__ together is because other really smart people in the Python community have developed really neat packages to make our lives easier. Listed below are the packages and versions used by __MMinte__. We highly recommend you check the development pages for these packages (you can just Google the package name and follow the links) to see other ways you can potentially use them in your own research, or to learn more about the work of the developers. Here is the list of packages/modules:

biopython==1.66

CherryPy==3.8.0

cobra==0.4.0b3

cycler==0.9.0

DataSpyre==0.2.0

Jinja2==2.8

MarkupSafe==0.23

matplotlib==1.5.0

numpy==1.10.1

pandas==0.17.1

pyparsing==2.0.6

python-dateutil==2.4.2

python-libsbml==5.12.0

pytz==2015.7

scipy==0.16.1

six==1.10.0

wheel==0.24.0

requests==2.8.1


####USAGE
#####How do I run MMinte?
1. Open the terminal window on your computer.
2. Go to the __MMinte__ folder by typing ``cd ~/Documents/MMinte_package/MMinte/``.
3. From this location type ``source env/bin/activate`` . This will activate your virtual environment. If you are not sure if your virtual environment is activated or not, you can check if the line of your prompt in the terminal has ``(env)`` in the beginning.
4. Go to the site folder by typing ``cd site``.
5. Launch __MMinte__ by typing ``python launchMMinte.py``
6. Open a web browser and go to the address http://127.0.0.1:8080/ . A window asking if you want to accept incoming network connections may pop up. You can just say yes to that. The following message shows up in the terminal, but you don't have to worry about it:
``CherryPy Checker:``
``The Application mounted at ' ' has an empty config.``
 
8. Play with __MMinte__. You can run a streamlined analysis or just individual widgets. Check out the tutorials for examples.
   - __PLEASE NOTE__: the path to your file and folder needs to be written correctly. Remember this is a relative path, and if you are wrting the path to folders, you need to end the path with a slash '/' 
9. When you are done, close the browser window and press CTRL+C on your terminal. This will terminate your __MMinte__ session. You should get your prompt back on the terminal window. You can also close the browser and use CTRL+C on your terminal at anytime to terminate __MMinte__. It may take a little longer for you to get your prompt back if you do this thought, since __MMinte__ will be cleaning up before shutting down.
10. You can then leave your virtual environment by typing ``deactivate``.
11. At this point, you can also close the terminal window (if you really want to.)


###MMinte command line examples
Note that these examples assume that you have the python packages cobra, os, itertools installed in your system outside the virtualenv.

__Reconstructing models in ModelSEED__
1. You should start by going into the site folder by typing ``cd ~/Documents/MMinte/site`` in the terminal.
2. Once there, start a python session by typing ``python``
3. Within python, import the widget3 by typing ``import widget3``
4. You can now use the function in widget 3 that allows you to reconstruct a model. All you need is a genomeID and a folder where your model will be stored. For instance, we will reconstruct a model for the species Bacteroides thetatiotaomicron VPI-5482 and store it in a folder named "CommandLineModels". Just type:
``import os``
``modelID = '22618.12'``
``modelFolder = '../CommandLineModels/'``
``if not os.path.exists(modelFolder): os.makedirs(modelFolder)`` press return twice
``widget3.getModels(modelID, modelFolder)``
5. You should be able to find that model in the CommandLineModels folder you just created.

__Creating a list of all possible pairwise combinations of the models in your models folder__

1. You should start by going into the site folder by typing ``cd ~/Documents/MMinte/site`` in the terminal.
2. Once there, start a python session by typing ``python``
3. Within python, import the widget3 by typing ``import widget4`` 
4. Import os and itertools to your session as well by typing ``import os,itertools``
5. Specify where your species models are (we will just use the modelFolder from the previous example): ``modelsFolder = '../CommandLineModels/'``
6. Speficy where you want the txt file with the list of pairs to go: ``outputFolder= '../pairsOfSpecies/'``
7. Specify what you want the text file with the list of pairs to be called: ``outputFile = 'listPairs.txt'``
8. Create the name of the path to your output files: ``output = outputFolder + outputFile``
9. Specify where the output file will go ``if not os.path.exists(outputFolder): os.makedirs(outputFolder)`` press return twice
10. Create the list with all pairs: ``widget4.createAllPairs(modelsFolder,output)``
11. You should find the list of pairs in the folder pairsOfSpecies.


__Creating a 2 species community model__
1. You should start by going into the site folder by typing ``cd ~/Documents/MMinte/site`` in the terminal.
2. Once there, start a python session by typing ``python``
3. Within python, import the widget3 by typing ``import widget4`` 
4. Import os and itertools to your session as well by typing ``import os,itertools``
5. Specify which species models you want use and where to find them: ``modelFileA = '../CommandLineModels/22618.12.sbml'`` and ``modelFileB = '../CommandLineModels/28116.7.sbml'``
6. Specify where you want to put the models. We will put these into a folder inside the CommandLineModels folder called CommunityModels: ``comFolder = '../CommandLineModels/CommunityModels/'``
7. If this folder doesn't exist, then create it: ``if not os.path.exists(comFolder): os.makedirs(comFolder)`` press return twice
8. Create the community model: ``widget4.createCommunityModel(modelFileA, modelFileB, comFolder)``

####SOME FAQS

#####What if I have installation issues?
Sometimes it may be troublesome to install new software in your local machine. Here we will list issues that users have had during installation and what the solution to fix them were. If you don't find a solution to your problem, raise an issue on github or send us a mail (microbialmetabolicinteractions@gmail.com). We will make our best to help you out.

1. __The user said:__ Typing virtualenv env on command line gave an error message: ImportError: dlopen(/Users/me/Documents/MMinte-master/MMinte/env/lib/python2.7/lib-dynload/_io.so, 2): Symbol not found: __PyCodecInfo_GetIncrementalDecoder
__The solution the user found was the following:__
 I could only fix it by downgrading from python 2.7.11 to 2.7.9, on a Mac Mavericks
2. __The user said:__ Starting MMinte then gave the following error:
File "/Users/me/Documents/MMinte-master/MMinte/env/lib/python2.7/locale.py", line 475, in _parse_localename, raise ValueError, 'unknown locale: %s' % localename
__The solution the user found was the following:__
I fixed this by adding the following two lines to my .bash_profile:
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8

#####What kind of files does MMinte need as an input?
The input files that are essential for __MMinte__ to start running are two:

1. File with associations between pairs of Operational Taxonomic Units (OTUs). This is a text file (.txt) that has, for each row, the identity of 2 OTUs and a measure of association between them. You can find and example file (corrs.txt) in the folder called userFiles . This file will contain only the information for the pairs of OTUs you, as a user, are interested in further exploring.
2. File with the sequences of representative OTUs in the FASTA format (.fasta). An example of this file (outs.fasta) can be found in the folder called userFiles . This file may contain the sequences for all the OTUs of a previous analysis you may have run, and so, a lot more OTU sequences than are really needed for the analysis. Widget 1 basically takes all these sequences and the information in file in point 1. to reduce the number of sequences to only the ones that are really necessary for the rest of the analysis

However, you can provide your own files for __MMinte__ to analyze in each widget. You can see some examples of these files in the folder exampleOutputs in the supportFiles folder. To know which file each widget takes as input, just open the widget and see which file is mentioned in the box on the left. If you want to make sure the widgets work, transfer the files in the exampleOutputs folder to the userOutput folder. __An exception__ is the file data4plot.json which you need to transfer to the site folder.

#####Where should my files go?
Your files can go anywhere in your system really. As long as you tell each widget where they are by writing the path to each them in the boxes on the left. 

#####Sometimes it seems that MMinte crashed. Is there a way for me to check how the program is going?
1. Go to the supportFiles folder
2. You can open the file logError_file.txt on any text editor, BUT,
3. If you want to keep track of things happening in real time, open the terminal and type the following ``cd ~/Documents/MMinte_package/MMinte/supportFiles ``, press enter, then type ``tail -f logError_file.txt`` and press enter. Your terminal will show you the last few lines of the logError_file.txt in real time, so you can see what the analysis is doing. When you don't want to see this anymore just press CTRL-C and you will be back at the prompt. If you still think there are problems, contact us at __microbialmetabolicinteractions@gmail.com__, and send us the logError_file.txt file,  so we can try to help. We want you to be able to use __MMinte__ and also make improvements, so please do not hesitate in contacting us.



####COPYRIGHT AND LICENSING INFORMATION

__MMinte__ is licensed under the following BSD 3-clause license: 

Copyright (c) 2016, Mayo Foundation for Medical Education and Research
All rights reserved.
Redistribution and noncommercial use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the Mayo Clinic nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.
For a license for commercial use, please contact Mayo Clinic Ventures at mayoclinicventures@mayo.edu.


