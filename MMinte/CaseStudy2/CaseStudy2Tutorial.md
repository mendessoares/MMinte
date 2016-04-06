###CaseStudy2 - Tutorial


Takes files:

* <b> ../CaseStudy2/ids4MS.txt</b>

This file contains a list of genome IDs for the bacterial species we are interested in. These are the species used in the study by [Rey et al. (2013)](http://www.pnas.org/content/110/33/13582.abstract).



These are the steps you need to take:

* Launch MMinte. Type ``` python lauchMMinte.py ``` on the terminal window.
* Open your favorite browser.
* Type <b>http://127.0.0.1:8080/</b> on the address field.
* Click on the tab that says <b>Widget 3</b>.

#### Widget 3
Metabolic models for each genome ID are reconstructed and gap-filled using [ModelSEED](http://modelseed.org/) and downloaded to the user’s local machine.

* On the field that asks whether you want to run the widget with the default example files type: <b>No</b>
* On the field asking for the path to the file that lists the IDs for the genomes that will be used to reconstruct the metabolic models type: <b> ../CaseStudy2/ids4MS.txt </b>
* On the field asking for a path to the folder where you are going to store the species models type (don't forget the slash): <b> ../CaseStudy2/output/models/ </b>

Each model takes on average 4 minutes to reconstruct, gap fill, and be exported to the your local machine. You can find the models for all the species identified as present in your dataset in the folder <b>../CaseStudy2/output/models/</b>


#### Widget 4
Metabolic models of 2-species communities are created using COBRA Toolbox for the python computational framework ([COBRApy](https://opencobra.github.io/)).

* On the field that asks whether you want to run the widget with the default example files type: <b>No</b> 
* Because we don't have a list of species to pair based on their IDs, on the field asking for the path to the file listing the species pairs type: '<b> NA </b>
* We also don't have a file with the correlations between pairs of OTUs. So, on the field asking for the path to the file with the information about the correlations between pairs of OTUs type: '<b>NA</b>'
* On the field that asks for the path to the models folder type: <b> ../CaseStudy2/output/models/ </b>
* On the field that asks for the path to the folder where the 2-species community metabolic models will be stored type: <b> ../CaseStudy2/output/comModels/</b>

Each 2-species community model takes abou 15 seconds to create. You can find all these models in the folder <b>../CaseStudy1/output/comModels/</b>



#### Widget 5
Under defined metabolic conditions, the growth rates of each species in isolation and when in the presence of another species in the community are estimated using flux balance analysis.

* On the field that asks whether you want to run the widget with the default example files type: <b>No</b>
* On the dropdown menu where you need to choose the metabolic conditions available for the optimization of the models choose: <b> Complete </b>
* On the field asking for the path for the 2-species models folder type: <b> ../CaseStudy2/output/comModels/ </b>
* On the field asking for the path to the results folder type: <b> ../CaseStudy2/output/ </b>
* Om the field asking for a name for the file that will contain the information about growth rates of the species in the presence and absence of another species in the community type: <b> growthRatesComplete.txt </b>

The Results tab will show the first 10 lines of the <b> growthRatesComplete.txt </b> file. You can find this file in the <b> ../CaseStudy2/output/ </b> folder.



#### Widget 6
The kinds of interactions occurring between the pairs of species on the metabolic conditions defined Widget 5 are predicted. The interactions are either positive (commensalism, mutualism) or negative (parasitism, amensalism, competition).

* On the field that asks whether you want to run the widget with the default example files type: <b>No</b>
* On the field asking for the path to the file predicting the growth rates of the species in the community type: <b> ../CaseStudy2/output/growthRatesComplete.txt </b>
* On the field asking for the path to the results folder type: <b> ../CaseStudy2/output/ </b>
* On the field asking for the name for the file that will have the types of interactions assigned to the pairs of species type: <b> interactionsComplete.txt </b>

The Results tab will show the first 10 lines of the <b> interactionsComplete.txt </b> file. You can find this file in the <b> ../CaseStudy2/output/ </b> folder.

