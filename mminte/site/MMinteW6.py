from spyre import server
from pkg_resources import resource_filename
from widget6 import evaluateInteractions
import os


import cherrypy
#cherrypy.config.update({"response.timeout":1000000,'log.access_file': '../supportFiles/logs/logAccess_file.txt', 'log.error_file': '../supportFiles/logs/logError_file.txt','log.screen':True})

class Widget6(server.App):
    title = 'Widget 6'
    
    inputs = [
        {"type": "text",
         "label": '<font size=4pt>In this widget we are going to characterize interactions based on how the growth of the bacteria changes in the presence or absence of another species. We label the interactions based on a table in the <a href = "http://aem.asm.org/content/81/12/4049.full">AEM paper by Almut Heinken and Ines Thiele</a>. What happens between two species may be broadly divided into positive, negative, or no interaction. </font> <br> <br>Do you want to just run the widget with the default example files?',
        "key": 'text20',
         "value": "Yes or No"},


        { "type":"text",
        "key":"text21",
        "label" : "<font size=3pt>Tell me where the file with predicted growth rates of the bacteria in the presence or absence of another species is</font>",
        "value":"Enter the path to the file with the predicted growth rates"},


        {"type": "text",
         "key": 'text22',
         "label": "<font size=3pt>Tell me which folder you would like to put the final table with the information about the predicted interactions between species in </font>",
         "value": "Enter the path to your results folder"},

        {"type": "text",
         "key": 'text23',
         "label": "<font size=3pt>Tell me what do you want the file with the final table with the predicted interactions to be called</font>",
         "value": "Enter the name of your file"}


              ]
    
    outputs = [{"type":"html",
                "id":"some_html",
                "control_id":"run_widget",
                "tab":"Results",
                "on_page_load": False}]
    
    controls = [{"type":"button",
                 "label":"Run Widget 6",
                 "id":"run_widget"}]
    
    tabs = ["Results"]
    
    def getCustomCSS(self):
        with open(resource_filename(__name__, 'static/custom_styleMMinte.css')) as style:
            return style.read()+'''\n .right-panel{width:65%;margin: 1em}'''
    
    def getHTML(self,params):

        if params['text20'] == 'Yes' or params['text1'] == "yes":
            inGRs = '../supportFiles/exampleRun/userOutput/growthRates.txt'
            outFolder = '../supportFiles/exampleRun/userOutput/'
            outInterFile = 'interactionsTable.txt'
            outInter = outFolder + outInterFile

        else:
            inGRs = params['text21']
            outFolder = params['text22']
            outInterFile = params['text23']
            outInter = outFolder + outInterFile


        if not os.path.exists(outFolder):
            os.makedirs(outFolder)

        
        try:
            cherrypy.log("We are starting the evaluation of interactions between pairs of organisms")
            evaluateInteractions(inGRs, outInter)
            cherrypy.log("Finished evaluating the interactions between the pairs of organisms")
            #fixme finishes calculating but doesn't show example output in results tab
        except:    
            cherrypy.log("We were unable to run evaluateInteractions.")
            return "Sorry something's wrong. Make sure the path to your file is correct."
            exit()
        



        
        
        head = ["<strong><font color=#00961E size=4pt>Hi. Here's a glimpse of what the first few lines of your Final Table look like.</strong></font>" ]
        head.append("<strong><font color=#00961E size=4pt> This table has all the information you need to do further analysis regarding the interactions on these species</strong></font>")
        head.append('<br>')
        head.append("<strong><font color=#00961E size=2pt>You can find this and the other files created here in the userOutput folder.</strong></font>")
        head.append('<br>')
        
        
        
        with open(outInter,'r') as myfile:
            top = [next(myfile) for x in xrange(10)]
        
        for i in top:
            head.append('<br>')
            head.append(i)
            
        return head
        
if __name__ == '__main__':
    app = Widget6()
    app.launch()
