import os
from pkg_resources import resource_filename
from widget1 import getUniqueOTU, getSeqs, workingOTUs
from widget2 import blastSeqs, listTaxId4ModelSEED
from widget3 import getModels
from widget4 import totalEXRxns,createEXmodel,createReverseEXmodel, addEXMets2SpeciesEX, replaceRxns,replaceMets,createCommunityModel,allPairComModels,createAllPairs,createSubsetPairs
from widget5 import getListOfModels,calculateGR
from widget6 import evaluateInteractions
from widget7 import nodes,links,createJSONforD3

from os import listdir
from os.path import isfile, join
import webbrowser


import cherrypy
from spyre import server

class custom_root(server.Root):
    @cherrypy.expose
    def widget7_out(self):
        with open(resource_filename(__name__, 'index.html')) as data:
            return data.read()

    @cherrypy.expose
    def d3(self):
        with open(resource_filename(__name__, 'd3.v3.min.js')) as data:
            return data.read()

    @cherrypy.expose
    def data4plot_json(self):
        with open(resource_filename(__name__, 'data2plot_json')) as data:
            return data.read()


server.Root=custom_root

class WidgetRunAll(server.App):
    title = 'Run All'

    inputs = [{"type": "text",
        "key": "text28",
        "label": "<font size=4pt>We're going to run the full pipeline for your data. You only need to give us two files</font><br><br><font size=3pt>The file that has the information about associated OTUs</font>",
         "value": "Enter the path to your file"},

        {"type": "text",
         "key": "text29",
         "label": "<font size=3pt>The file that has the sequences of the representative OTUs</font>",
         "value": "Enter the path to your file"},

        {"type":"dropdown",
        "key":'dropdown2',
        "label" : "<font size=3pt> Do you want the network to be plotted in this browser tab or in a new one </font>",
        "options" :[{"label": "This one", "value":"Current"},
                    {"label": "New one", "value":"New"}],
                    "value":'Current'}
    ]

    outputs = [{"type":"html",
                "id":"some_html",
                "control_id":"run_widget",
                "tab":"Results",
                "on_page_load": False}]

    controls = [{"type":"button",
                 "label":"Run Full Analysis",
                 "id":"run_widget"}]

    tabs = ["Results"]


    def getCustomCSS(self):
        with open(resource_filename(__name__, 'static/custom_styleMMinte.css')) as style:
            return style.read()+'''\n .right-panel{width:65%;margin: 1em}'''




    def getHTML(self,params):
        corrsFile = params['text28']
        sequencesFile = params['text29']

        cherrypy.log("We will run the full analysis.")

        '''
        Run Widget 1
        '''

        if not os.path.exists('../fullRun/userOutput/'):
            os.makedirs('../fullRun/userOutput/')

        outputFasta = '../fullRun/userOutput/reprOTUs.fasta'

        cherrypy.log("We're going to start running Widget 1. The files we are using are %s for the correlations and %s for the sequences. The output, that is the reduced dataset can be found in %s." %(corrsFile,sequencesFile,outputFasta))

        try:
            corrs = getUniqueOTU(corrsFile)
        except:
            cherrypy.log("We were unable to run getUniqueOTU.")
            return "Sorry something's wrong. Make sure the path to your file is correct."
            exit()

        try:
            seqs = getSeqs(sequencesFile)
        except:
            cherrypy.log("We were unable to run getSeqs.")
            return "Sorry something's wrong. Make sure the path to your file is correct."
            exit()

        try:
            workingOTUs(corrs,seqs,outputFasta)
        except:
            cherrypy.log("We were unable to run workingOTUs.")
            return "Sorry something's wrong. Make sure the path to your file is correct."
            exit()

        cherrypy.log('We successfully finished running Widget 1.')



        '''
        Run Widget 2
        '''


        tempOutputFile = '../fullRun/tempFiles/blastOutput.txt'
        seqsToBlast = '../fullRun/userOutput/reprOTUs.fasta'
        outputSimil = '../fullRun/userOutput/simil.txt'
        outputIDs = '../fullRun/userOutput/ids4MS.txt'

        cherrypy.log('We will now start running Widget 2. We will be blasting the sequences in %s and creating a file with the percent similarity between the query sequences and the sequences they matched to in %s . We will output a list of genome IDs to be collected from modelSEED to %s .' %(seqsToBlast,outputSimil,outputIDs))

        blastSeqs(seqsToBlast)

        cherrypy.log('Finished blasting the sequences.')

        listTaxId4ModelSEED(outputSimil,outputIDs)

        cherrypy.log('Finished running Widget 2.')

        '''
        Run Widget 3
        '''

        modelFolder = '../fullRun/userOutput/models/'
        listIDs = '../fullRun/userOutput/ids4MS.txt'

        cherrypy.log('Will now run Widget 3. We will go over the genome IDs in %s and reconstruct metabolic models for those species. We will put all the models in %s .' %(listIDs, modelFolder))


        if not os.path.exists(modelFolder):
            os.makedirs(modelFolder)


        listOfModels = open(listIDs,'r')
        mypath = modelFolder

        existingModels = [f for f in listdir(mypath) if isfile(join(mypath, f))]


        for i in listOfModels:
            cherrypy.log("Will now see if %s is in the folder already" %i)
            i = i.rstrip()
            if (i + '.sbml') not in existingModels:
                cherrypy.log("The model %s isn't in the folder, so we're going to fetch it from ModelSeed" %i)
                try:
                    cherrypy.log("Started getting model for genome %s" %i)
                    getModels(i,modelFolder)
                    cherrypy.log("We finished getting the metabolic model for genome %s from ModelSEED." %i)
                except:
                    #cherrypy.log("We were either unable to run getModels or were unable to get the metabolic models we wanted from ModelSEED. We'll keep going for now and try the next model.")
                    #return "Sorry something's wrong. Make sure the path to your file is correct."
                    pass
                continue
            else:
                cherrypy.log("The model %s was already in the folder" %i)
                continue

        cherrypy.log('We were are done reconstructing the metabolic models and exporting them to the local machine. Therefore, we are done running Widget 3.')

        '''
        Run Widget 4
        '''

        comFolder = '../fullRun/userOutput/comModels/'
        modelFolder = '../fullRun/userOutput/models/'
        similFile = '../fullRun/userOutput/simil.txt'

        cherrypy.log('We will now run Widget 4. ')

        if not os.path.exists(comFolder):
            os.makedirs(comFolder)


        createSubsetPairs(similFile,corrsFile)


        pairsList = '../tempFiles/pairsList.txt'

        allPairComModels(pairsList,modelFolder,comFolder)


        '''
        Run Widget 5
        '''
        food = 'Complete'
        outputGRs = '../fullRun/userOutput/GRsComplete.txt'
        comFolder = '../fullRun/userOutput/comModels/'


        calculateGR(food, outputGRs, comFolder)

        '''
        Run Widget 6
        '''

        inGRs = '../fullRun/userOutput/GRsComplete.txt'
        outInter = '../fullRun/userOutput/interactionsComplete.txt'


        evaluateInteractions(inGRs, outInter)


        '''
        Run Widget 7
        '''

        inNodes = '../fullRun/userOutput/simil.txt'
        inLinks = corrsFile
        inInter = '../fullRun/userOutput/interactionsComplete.txt'

        node = nodes(inNodes)
        link = links(inNodes,inLinks,inInter)

        createJSONforD3(node,link)


        ROOT_DIR = os.path.dirname(os.path.realpath('index.html'))
        full_path = ROOT_DIR + '/index.html'


        script='''<style>

.node {
  stroke: #fff;
  stroke-width: 1.5px;
}

.link {
  stroke: #999;
  stroke-opacity: .6;
}

</style>

<script src="d3"></script> <!-- changed this from the source in the website to be local source -->
<script window.onload>


    height = 800;

var colorNodes = d3.scale.linear()
      .domain([1,2,3,4,5,6])
      .range(["#3d3d3d","4a4a4a","565656", "#636363", "#707070","#d9d9d9"]); <!-- colors for nodes -->


var colorLinks = d3.scale.linear()
    .domain([2,1,0])
    .range(["#2ca02c","#d62728","#c7c7c7"]); <!-- colors for links, green, red, grey -->





document.onload=d3.json("data4plot_json", function(error, graph) {
  var width=document.getElementById('some_html').offsetWidth;
var force = d3.layout.force()
    .charge(-150)
    .size([width, height])
   	.linkDistance(function(link) {
       return link.value*20;
    });
  var svg = d3.select("body").select("#some_html").append("svg")
    .attr("width", width)
    .attr("height", height);
  if (error) throw error;


  force
      .nodes(graph.nodes)
      .links(graph.links)
      .start();



  var link = svg.selectAll(".link")
      .data(graph.links)
      .enter().append("line")
      .attr("class", "link")
      .style("stroke-width", function(d) { return (6*1/d.value); })
      .style("stroke", function(d) {return colorLinks(d.interaction);});

  var node = svg.selectAll(".node")
      .data(graph.nodes)
    .enter().append("circle")
      .attr("class", "node")
      .attr("r", 5)
      .style("fill", function(d) { return colorNodes(d.group); })
      .call(force.drag);

  node.append("title")
      .text(function(d) { return d.name; });

  force.on("tick", function() {
    link.attr("x1", function(d) { return d.source.x; })
        .attr("y1", function(d) { return d.source.y; })
        .attr("x2", function(d) { return d.target.x; })
        .attr("y2", function(d) { return d.target.y; });

    node.attr("cx", function(d) { return d.x; })
        .attr("cy", function(d) { return d.y; });
  });
});

</script>
'''
        head = ["The plot with the network of interactions between your favorite organisms is shown on a new tab."]
        head.append('<br>')
        head.append('<br>')
        head.append('<br>')
        head.append("The shading of the nodes indicates how close the sequence of the OTU is to the sequence of the genome. The darker the node, the higher the similarity.")
        head.append('<br>')
        head.append('<br>')
        head.append('<br>')
        head.append("The length and thickness of the links reflect the association values on the initial file you provided. The shorter and thicker the link, the higher the association value.")
        head.append('<br>')
        head.append('<br>')
        head.append('<br>')
        head.append("The colors of the links reflect the kind of interaction. The red, green and grey represent negative, positive and no interaction, respectively.")
        head.append('<br>')
        head.append('<br>')
        head.append('<br>')
        head.append('<a href="http://d3js.org/" >D3 is awesome</a>! If you mouse over the nodes, you get the id of the OTU, and if you click a node and drag it, the network will follow it.')
        head.append("You can find all the intermediate files in the folder called fullRun.")


        if params['dropdown2'] == 'Current':
            head.append(script)
        else:
            webbrowser.open('http://localhost:8080/widget7_out',new=1)

        return head

        return head




if __name__ == '__main__':
    app = WidgetRunAll()
    app.launch()