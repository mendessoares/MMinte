from spyre import server
from pkg_resources import resource_filename
from widget4 import totalEXRxns,createEXmodel,createReverseEXmodel, addEXMets2SpeciesEX, replaceRxns,replaceMets,createCommunityModel,allPairComModels,createAllPairs,createSubsetPairs
import os, os.path

import cherrypy
#cherrypy.config.update({"response.timeout":1000000,'log.access_file': '../supportFiles/logs/logAccess_file.txt','log.error_file': '../supportFiles/logs/logError_file.txt','log.screen':True})

class Widget4(server.App):
    title = 'Widget 4'
    
    inputs = [
        {"type": "text",
         "label": "<font size=4pt>In this widget we are going  we're just going to create 2-species community metabolic models based on a file that lists the pairs of species that should go together. These are either the ones listed in file with correlations between pairs of species, or, if you don't provide a file with correlations between pairs of species, all possible unique combinations between the bacteria in your list of species.</font> <br> <br>Do you want to just run the widget with the default example files?",
        "key": 'text14',
        "value": "Yes or No"},

        { "type":"text",
        "key":"text15",
        "label" : "<font size=3pt> Tell me what the path to the file that has a list of species to pair. If you don't have this and just want to create all possible 2-species communities with the models in your models folder, just type: NA.  </font>",
        "value":"Enter path to file listing the species pairs"},

        { "type":"text",
        "key":"text28",
        "label" : "<font size=3pt> We can also create a list of pairs based on level of correlation between the OTUs in the analysis and the similarity between these OTUs and the genomeID they were associated with in widget 2. Tell me which file has the information about the <b>correlations</b> between pairs of <b>OTUs</b>. Again, if you just want to create all possible 2-species communities with the models in your models folder, just type: NA. </font>",
        "value":"Enter the path to the correlations file here"},

        { "type":"text",
        "key":"text29",
        "label" : "<font size=3pt> Tell me which file has the information about the percent similarity between the OTUs analyzed and the genome they were matched with (one of the outputs of Widget 2). Again, if you just want to create all possible 2-species communities with the models in your models folder, just type: NA.</font>",
        "value":"Enter the path to the percent similarity file here"},


        { "type":"text",
        "key":"text16",
        "label" : "<font size=3pt> Please tell me the path to the folder containing the metabolic models you want to use. </font>",
        "value":"Enter path to your model folder"},

        {"type": "text",
         "key": 'text17',
         "label": "<font size=3pt>Tell me which folder you would like to put models of the 2-species communities</font>",
         "value": "Enter the path to your communities folder"},
        ]
    
    outputs = [{"type":"html",
                "id":"some_html",
                "control_id":"run_widget",
                "tab":"Results",
                "on_page_load": False}]
    
    controls = [{"type":"button",
                 "label":"Run Widget 4",
                 "id":"run_widget"}]
    
    tabs = ["Results"]
    
    def getCustomCSS(self):
        with open(resource_filename(__name__, 'static/custom_styleMMinte.css')) as style:
            return style.read()+'''\n .right-panel{width:65%;margin: 1em}'''
        
        
    def getHTML(self,params):

        if params['text14'] == 'Yes' or params['text1'] == "yes":
            #list @todo fix this!!! Hacked!
            corrsFile = '../supportFiles/exampleRun/userFiles/corrs.txt'
            similFile = '../supportFiles/exampleRun/userOutput/similFile.txt'
            modelFolder = '../supportFiles/exampleRun/userOutput/models/'
            comFolder = '../supportFiles/exampleRun/userOutput/communityModels/'
            createSubsetPairs(similFile,corrsFile)
            list = '../tempFiles/pairsList.txt'

        else:
            list = params['text15'] #todo, create this on the fly from the list of speciesIDs
            corrsFile = params['text28']
            similFile = params['text29']
            modelFolder = params['text16']
            comFolder = params['text17']

        ############## In case there is no list to start with! #############

        if list == 'NA' and similFile == 'NA' and corrsFile == 'NA':
            createAllPairs(modelFolder)
            list = '../tempFiles/pairsList.txt'
        elif list == 'NA' and similFile != 'NA' and corrsFile != 'NA':
            createSubsetPairs(similFile,corrsFile)
            list = '../tempFiles/pairsList.txt'

        ############## Ok, now there is a list #############################






        if not os.path.exists(comFolder):
            os.makedirs(comFolder)

        try:
            allPairComModels(list,modelFolder,comFolder)
            cherrypy.log("We're finished creating your community models")
        except:
            cherrypy.log("We were unable to run allPairComModels.")
            return "Sorry something's wrong. Make sure the path to your file is correct and that the python module cobrapy is loaded into your system."
            exit()
        
        
        numModels = sum(os.path.isfile(os.path.join(comFolder, f)) for f in os.listdir(comFolder)) - 1
        
        
        
        return "We created %d community models. In the next widget, we will use them  to predict the growth rate of their species in isolation and when in the community using COBRA tools. You can find all the models in the %s." %(numModels,comFolder)


if __name__ == '__main__':
    app = Widget4()
    app.launch()
