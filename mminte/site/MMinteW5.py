from spyre import server
from widget5 import getListOfModels,calculateGR
import os

import cherrypy
#cherrypy.config.update({"response.timeout":1000000,'log.access_file': '../supportFiles/logs/logAccess_file.txt','log.error_file': '../supportFiles/logs/logError_file.txt','log.screen':True})

class Widget5(server.App):
    title = 'Widget 5'
    
    inputs = [
        {"type": "text",
         "label": "<font size=4pt>In this widget we're going to calculate growth rates for the species in each community. Because we will want to know how the presence of another species in the community affects the growth of a particular organism, we will estimate how the species grow when in the absence and presence of another species in the community under particular nutritional conditions. A table with the growth rates of each species in the community and in isolation will be created. </font> <br> <br>Do you want to just run the widget with the default example files?",
        "key": 'text16',
         "value": "Yes or No"},

        { "type":"dropdown",
        "key":"dropdown1",
        "label" : "<font size=3pt> You can determine which kind of metabolites are available for the organisms by choosing a diet. In the 'Complete' diet, 380 metabolites are available to the model, with a flux for the import reactions of 100 mmol/gDW/hr. 'Variant 1' contains the same metabolites, but the reaction fluxes are 10 mmol/gDW/hr, and in 'Variant 2' the fluxes are 1 mmol/gDW/hr. The other Variants are place holders for user defined diets.</font>",
        "options" :[{"label": "Complete", "value":"Complete"},
                    {"label": "Variant 1", "value":"Variant1"},
                    {"label": "Variant 2", "value":"Variant2"},
                    {"label":"Variant 3","value":"Variant3"},
                    {"label":"Variant 4","value":"Variant4"},
                    {"label":"Variant 5","value":"Variant5"},
                    {"label":"Variant 6","value":"Variant6"},
                    {"label":"Variant 7","value":"Variant7"},
                    {"label":"Variant 8","value":"Variant8"},
                    {"label":"Variant 9","value":"Variant9"},
                    {"label":"Variant 10","value":"Variant10"}],
                    "value":'Complete'},

        {"type": "text",
         "key": 'text17',
         "label": "<font size=3pt>Tell me which you folder has the community models we will use in this analysis</font>",
         "value": "Enter the path to your 2-species models folder"},

        {"type": "text",
         "key": 'text18',
         "label": "<font size=3pt>Tell me which you folder would like to put the table with the results from your analysis in</font>",
         "value": "Enter the path to your results folder"},

        {"type": "text",
         "key": 'text19',
         "label": "<font size=3pt>Tell me what do you want the file containing the table with the growth rates to be called</font>",
         "value": "Enter the name of your file"}
              ]
    
    outputs = [{"type":"html",
                "id":"some_html",
                "control_id":"run_widget",
                "tab":"Results",
                "on_page_load": False}]
    
    controls = [{"type":"button",
                 "label":"Run Widget 5",
                 "id":"run_widget"}]
    
    tabs = ["Results"]
    
    def getCustomCSS(self):
        ROOT_DIR = os.path.dirname(os.path.realpath('static/custom_styleMMinte.css'))
        with open(ROOT_DIR + '/custom_styleMMinte.css') as style:
            return style.read()+'''\n .right-panel{width:65%;margin: 1em}'''
    
    def getHTML(self,params):

        if params['text16'] == 'Yes' or params['text1'] == "yes":
            food = 'Complete'
            comFolder = '../supportFiles/exampleRun/userOutput/communityModels/'
            outFolder = '../supportFiles/exampleRun/userOutput/'
            outGRsFile = 'growthRates.txt'
            outputGRs = outFolder + outGRsFile


        else:
            food = params['dropdown1']
            comFolder = params['text17']
            outFolder = params['text18']
            outGRsFile = params['text19']
            outputGRs = outFolder + outGRsFile


        if not os.path.exists(outFolder):
            os.makedirs(outFolder)

        
        try:
            cherrypy.log("We are starting the growth rate calculation")
            calculateGR(food, outputGRs, comFolder)
            cherrypy.log("Finished calculating the growth rates of the species")
            #fixme it's not showing the output on the results window even though it's done

        except:
            cherrypy.log("We were unable to run calculateGR.")
            return "Sorry something's wrong. Make sure the path to your file is correct."
            exit()
         
        
        head = ["<strong><font color=#00961E size=4pt>Here's a glimpse of what the first few lines of your growth rates file look like.</strong></font>"]
        head.append('<br>')
        head.append("<strong><font color=#00961E size=2pt>You can find this and the other files created here in the userOutput folder.</strong></font>")
        head.append('<br>')
        
    
        
        with open(outputGRs,'r') as myfile:
            top = [next(myfile) for x in xrange(10)]
        
        for i in top:
            head.append('<br>')
            head.append(i)
           
            
        return head

if __name__ == '__main__':
    app = Widget5()
    app.launch()
