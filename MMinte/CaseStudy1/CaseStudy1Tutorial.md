###CaseStudy1 - Tutorial


Takes files:

* <b> ../CaseStudy1/userFiles/corrs.txt</b>
* <b> ../CaseStudy1/userFiles/seqs.fasta</b>

These are the steps you need to take:

* Launch MMinte. Type ``` python lauchMMinte.py ``` on the terminal window.
* Open your favorite browser.
* Type <b>http://127.0.0.1:8080/</b> on the address field.
* Click on the tab that says <b>Widget 1</b>.
#### Widget 1
This Widget performs a data reduction step. Using information about pairs of operational taxonomic units (OTUs) that are associated to some degree and a list of 16S rDNA sequences for the OTUs in a particular community, a file is created containing only the sequences for representative OTUs significant to the analyses.

* On the field that asks whether you want to run the widget with the default example files type: <b>No</b>
* On the field that asks about the path to the associated OTUs file type: <b>../CaseStudy1/userFiles/corrs.txt</b> 

	You can check this file by going to the CaseStudy1 folder and opening the corrsFlat.txt file in any text editor. Here is what the header and first five lines of dat this file looks like:
	
	OtuA	OtuB	Correlation<br>
	OTU_97.10268	OTU_97.1027	1<br>
	OTU_97.10269	OTU_97.10270	1<br>
	OTU_97.10268	OTU_97.10271	1<br>
	OTU_97.1027	OTU_97.10271	1<br>
	OTU_97.10269	OTU_97.10272	1<br>	
	
* On the field that asks about the path to the sequences of the representative OTUs type: <b>../CaseStudy1/userFiles/seqs.fasta</b>

	You can check this file by going to the CaseStudy1 folder and opening the rep_set.fna file in any text editor. Here is what this file looks like:
	

\>OTU_97.1 SRS014778.SRX020554_796412735<br>
CACGTAGTTAGCCGTGACTTTCTGGTTGATTACCGTCAAATAAAGGCCAGTTACTACCTCTATCCTTCTTCACCAACAACAGAGCTTTAC<br>GATCCGAAAACCTTCTTCACTCACGCGGCGTTGCTCCATCAGACTTGCGTCCATTGTGGAAGATTCCCTACTGCTGCCTCCCGTAGGAGT<br>TTGGGCCGTGTCTCAGTCCCAATGTGGCCGATCAGTCTCTCAACTCGGCTATGCATCATCGCCTTGGTAAGCCTTTTACCTTACCAACTA<br>GCTAATGCACCGCGGGGGCCATTCCATAGCGACAGCTTACGCCGCCTTTTAAAAGCTGATCATGCGATCTGCTTTCTTATCCGGTATTAGCACCTGTTTCCAAGTGGTATCCCAGACTATGGGGCAGGTTCCCCACGTGTTACTCACCCACTCCGCCGCTCGCTTCCTACGTCATACGAG<br>GTAAATCTGTTAGTTCCGCTCGCTCGACTTGCATGTATTAGGC<br>

\>OTU_97.10 SRS014321.SRX020546_563326764<br>
CACGTAGTTAGCCGTGGCTTTCTATTCCGGTACCGTCAATCCTTCTAACTATTCGCAAGAAGGCCTTTCGTCCCGATTAACAGAGCTTTA<br>CAACCCGAAGGCCGTCATCACTCACGCGGCGTTGCTCCGTCAGACTTTCGTCCATTGCGGAAGATTCCCCACTGCTGCCTCCCGTAGGAG<br>TCTGGGCCGTGTCTCAGTCCCAATGTGGCCGTTCATCCTCTCAGACCGGCTACTGATCATCGCCTTGGTGGGCCGTTACCCCTCCAACTA<br>GCTAATCAGACGCAATCCCCTCCTTCAGTGATAGCTTACATGTAGACGGCCTACCTTTCATCTATCCTCGATGCCGAGGTTAGATCGTAT<br>GCGGTACTTAGCAGTCGTTTCCAACTGTTGTCCCCCTCTGAACGGGTCAGGTTGATTACGCGTTACTCACCCGTTCGCCACTAAGATTGA<br>CTTAGAAGCAAGCTTACCATCGCTCTTCGTTCGACTTCGCATCGTGTTAAGCTACGCCGCCAGG<br>

\>OTU_97.100 SRS014562.SRX020546_151039577<br>
CACGTAGTTAGCCGTGGCTTTCTCTTACGGTACCGTCACTTCTTATGGGTATTAACCACAAGACTATTCGTCCCGTATAACAGAGCTTTA<br>CAACCCGAAGGCCGTCTTCACTCACGCGGCGTTGCTCCGTCAGGCTTTCGCCCATTGCGGAAGATTCCCCACTGCTGCCTCCCGTAGGAG<br>TCTGGACCGTGTCTCAGTTCCAATGTGGCCGTTCATCCTCTCAGACCGGCTACTGATCGTCGCCTTGGTGGGCCGTTACCCCTCCAACTA<br>GCTAATCAGACGCAAACCCCTCCTCCGGCGATAGCTTATAAATAGAGGCCATCCTTTCTTCCGACAGTCATGCGACTTTCGGAACGTATT<br>CGGTATTAGCAGCCGTTTCCAGCTGTTGTCCCCATCCGTAGGGCAGGTTGTTTACGCGTTACTCACCCGTTTGCCACTAGATTGTAGAAA<br>AAGCAAGCTTTCTCTACGCTCTCGTTCGACTTGCATGTGTTAAGCACGCCGCCAGCGTCGTCCTCGTAGCGTACGACG<br>
\>OTU_97.1000 SRS015131.SRX020546_570672733<br>
CACGTAGTTAGCCGGTGCTTATTCTTCCGGTACCGTCAGCACGCAATGGTATTAACATCGCGCTTTTCTTCCCGGACAAAAGTCCTTTAC<br>AACCCGAAGGCCTTCTTCAGACACGCGGCATGGCTGGATCAGGGTTGCCCCCATTGTCCAAAATTCCCCACTGCTGCCTCCCGTAGGAGT<br>CTGGGCCGTGTCTCAGTCCCAGTGTGGCGGATCATCCTCTCAGACCCGCTACTGATCGTCGCCTTGGTAGGCCTTTACCCCACCAACCAG<br>CTAATCAGATATCGGCCGCTCCAATAGCGCGAGGTCCGAAGATCCCCCGCTTTCACCCTCAGGTCGTATGCGGTATTAATCCGGCTTTCG<br>CCGAGCTATCCCCCACTACTGGGCACGTTCCGATGTATTACTCACCCGTTCGCCACTCGCCGCCAGGCCGAAGCCCGCGCTGCCGTTCGA<br>CTTGCATGTGTAAAGCATGCCGCCAGCGTTCAATCTGAGCCAGGATCAACTCTCTG<br>CACCTGTTTCCAAGTGGTATCCCAGACTATGGGGCAGGTTCCCCACGTGTTACTCACCCACTCCGCCGCTCGCTTCCTACGTCATACGAG<br>GTAAATCTGTTAGTTCCGCTCGCTCGACTTGCATGTATTAGGC<br><br>

* On the field asking for the path to your results folder type (make sure you add the slash in the end): <b>../CaseStudy1/output/</b> <br>
* On the field asking for a file name for the results file type:
<br> <b> repSeqs.fasta </b> <br>
* Click the button that says <b>Run Widget 1</b>

The Resuls tab will show the contents of the file created. This file is called <b> repSeqs.fasta </b> and you can find it in the folder <b> ../CaseStudy1/output/ </b> . This file contains the subset of sequences that correspond to the OTUs present in the corrs.txt file. Next, click on the tab that says <b> Widget 2</b>.

#### Widget 2
In this Widget the sequences of your favorite representative OTUs are matched to a genome ID. The representative OTUs are identified and assigned a genome ID using BLAST and a local database containing the 16S rDNA sequences of species with whole genome sequences.

* On the field that asks whether you want to run the widget with the default example files type: <b>No</b>
* On the field asking for the path to the file that has the sequences you want to get the genome ID for type: <b> ../CaseStudy1/output/repSeqs.fasta</b>
* On the field asking for the path to your results folder type: <b> ../CaseStudy1/output/</b>
* On the field asking you for a name for the file that will have the similarity information type: <b> simil.txt </b>
* On the field asking you for a name for the file that will have the list of genome IDs type: <b> listIDs.txt </b>

The Resuls tab will show the contents of the file with the list of IDs for the genomes we will use to reconstruct and gap fill metabolic models. This file is called <b> listIDs.txt </b> and you can find it in the folder <b> ../CaseStudy1/output/ </b> .  Next, click on the tab that says <b> Widget 3</b>.


#### Widget 3
Metabolic models for each genome ID are reconstructed and gap-filled using [ModelSEED](http://modelseed.org/) and downloaded to the user’s local machine.

* On the field that asks whether you want to run the widget with the default example files type: <b>No</b>
* On the field asking for the path to the file that lists the IDs for the genomes that will be used to reconstruct the metabolic models type: <b> ../CaseStudy1/output/listIDs.txt </b>
* On the field asking for a path to the folder where you are going to store the species models type (don't forget the slash): <b> ../CaseStudy1/output/models/ </b>

Each model takes on average 4 minutes to reconstruct, gap fill, and be exported to the your local machine. You can find the models for all the species identified as present in your dataset in the folder <b>../CaseStudy1/output/models/</b>


#### Widget 4
Metabolic models of 2-species communities are created using COBRA Toolbox for the python computational framework ([COBRApy](https://opencobra.github.io/)).

* On the field that asks whether you want to run the widget with the default example files type: <b>No</b> 
* Because we don't have a list of species to pair based on their IDs, on the field asking for the path to the file listing the species pairs type: '<b> NA </b>
* However, we do have a file with the correlations between pairs of OTUs. So, on the field asking for the path to the file with the information about the correlations between pairs of OTUs type: <b> ../CaseStudy1/userFiles/corrs.txt </b>
* On the filed that asks for the path to the models folder type: <b> ../CaseStudy1/output/models/ </b>
* On the filed that asks for the path to the folder where the 2-species community metabolic models will be stored type: <b> ../CaseStudy1/output/comModels/</b>

Each 2-species community model takes abou 15 seconds to create. You can find all these models in the folder <b>../CaseStudy1/output/comModels/</b>



#### Widget 5
Under defined metabolic conditions, the growth rates of each species in isolation and when in the presence of another species in the community are estimated using flux balance analysis.

* On the field that asks whether you want to run the widget with the default example files type: <b>No</b>
* On the dropdown menu where you need to choose the metabolic conditions available for the optimization of the models choose: <b> Complete </b>
* On the field asking for the path for the 2-species models folder type: <b> ../CaseStudy1/output/comModels/ </b>
* On the field asking for the path to the results folder type: <b> ../CaseStudy1/output/ </b>
* Om the field asking for a name for the file that will contain the information about growth rates of the species in the presence and absence of another species in the community type: <b> growthRatesComplete.txt </b>

The Results tab will show the first 10 lines of the <b> growthRatesComplete.txt </b> file. You can find this file in the <b> ../CaseStudy1/output/ </b> folder.



#### Widget 6
The kinds of interactions occurring between the pairs of species on the metabolic conditions defined Widget 5 are predicted. The interactions are either positive (commensalism, mutualism) or negative (parasitism, amensalism, competition).

* On the field that asks whether you want to run the widget with the default example files type: <b>No</b>
* On the field asking for the path to the file predicting the growth rates of the species in the community type: <b> ../CaseStudy1/output/growthRatesComplete.txt </b>
* On the field asking for the path to the results folder type: <b> ../CaseStudy1/output/ </b>
* On the field asking for the name for the file that will have the types of interactions assigned to the pairs of species type: <b> interactionsComplete.txt </b>

The Results tab will show the first 10 lines of the <b> interactionsComplete.txt </b> file. You can find this file in the <b> ../CaseStudy1/output/ </b> folder.


#### Widget 7
A network is plotted with [D3.js](https://d3js.org/) using the initial information of associations between the pairs of OTUs provided by the user, and the kinds of interactions predicted to be occurring are layed over the links. Links colored red mean the interaction between the two linked OTUs is predicted to be negative. Links colored gree mean the interaction between the two linked OTUs is predicted to be positive. Links colored grey mean no interaction is predicted to occur between the two linked OTUs. The shading of the nodes reflects the level of similarity between the sequence of the OTU (query sequence) and the sequence it was matched with from a full genome (matched sequence). The lighter the node, the less similar is the query sequence to the matched sequence.


* On the field that asks whether you want to run the widget with the default example files type: <b>No</b>
* On the dropdown menu where you need to choose where to plot the network choose '<b>New one</b>'
* On the field asking for the path to the percent similarity file type: <b> ../CaseStudy1/output/simil.txt </b>
* On the field asking for the path to the file containing the information about how the OTUs are correlated type: <b> ../CaseStudy1/userFiles/corrs.txt </b>
* On the field asking for the path to the file containing the information about the interactions between the different species type: <b> ../CaseStudy1/output/interactionsComplete.txt </b>

The Results tab will show an short explanation of the  network plot. The network itself will be shown in a new tab that opens automatically. 