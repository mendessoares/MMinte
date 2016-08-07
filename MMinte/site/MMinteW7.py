from spyre import server
from widget7 import nodes,links,createJSONforD3
import os
import webbrowser

import cherrypy
#cherrypy.config.update({"response.timeout":1000000,'log.access_file': '../supportFiles/logs/logAccess_file.txt','log.error_file': '../supportFiles/logs/logError_file.txt','log.screen':True})

import cherrypy
class custom_root(server.Root):
    @cherrypy.expose
    def widget7_out(self):
		ROOT_DIR = os.path.dirname(os.path.realpath('index.html'))
		full_path = ROOT_DIR + '/index.html'
		with open(full_path) as data:
			return data.read()
    @cherrypy.expose
    def d3(self):
		ROOT_DIR = os.path.dirname(os.path.realpath('d3.v3.min.js'))
		full_path = ROOT_DIR + '/d3.v3.min.js'
		with open(full_path) as data:
			return data.read()
    @cherrypy.expose
    def data4plot_json(self):
		ROOT_DIR = os.path.dirname(os.path.realpath('data4plot_json'))
		full_path = ROOT_DIR + '/data4plot_json'
		with open(full_path) as data:
			return data.read()
			
server.Root=custom_root
			
	
class Widget7(server.App):
    title = 'Widget 7'
    
    inputs = [{"type": "text",
        "label": '<font size=4pt>And last, but not least, we will plot a network where the nodes represent the different OTUs and the length and thickness of links represent the correlations in your initial files. The color of the links will represent the kind of interaction predicted between those two OTUs by MMinte. We will do this using <a href="https://d3js.org/">D3</a>, a neat "JavaScript library for manipulating documents based on data".  </font> <br> <br>Do you want to just run the widget with the default example files?',
        "key": 'text24',
        "value": "Yes or No"},

       {"type":"dropdown",
        "key":"dropdown2",
        "label" : "<font size=3pt> Do you want the network to be plotted in this browser tab or in a new one </font>",
        "options" :[{"label": "This one", "value":"Current"},
                    {"label": "New one", "value":"New"}],
                    "value":'Current'},


        {"type":"text",
        "key":"text25",
        "label" : "<font size=3pt> Tell me which file has the information about the percent similarity between the OTUs analyzed and the genome they were matched with (one of the outputs of Widget 2) </font>",
        "value":"Enter the path to the percent similarity file here"},

        {"type":"text",
        "key":"text26",
        "label" : "<font size=3pt> Tell me which file has the information about the <b>correlations</b> between pairs of <b>OTUs</b>.</font>",
        "value":"Enter the path to the correlations file here"},

        { "type":"text",
        "key":"text27",
        "label" : "<font size=3pt> Tell me which file has the information about the type of interactions occurring between pairs of <b> species </b> </font>",
        "value":"Enter the path to the interactions table here"}
              ]


    outputs = [{"type":"html",
                "id":"some_html",
                "control_id":"run_widget",
                "tab":"Results",
                "on_page_load": False}]
    
    controls = [{"type":"button",
                 "label":"Run Widget 7",
                 "id":"run_widget"}]
    
    tabs = ["Results"]
    
    def getCustomCSS(self):
        ROOT_DIR = os.path.dirname(os.path.realpath('static/custom_styleMMinte.css'))
        with open(ROOT_DIR + '/custom_styleMMinte.css') as style:
            return style.read()+'''\n .right-panel{width:65%;margin: 1em}'''
        
        
    def getHTML(self,params):

        if params['text24'] == 'Yes' or params['text1'] == "yes":
            inNodes = '../supportFiles/exampleRun/userOutput/similFile.txt'
            inLinks = '../supportFiles/exampleRun/userFiles/corrs.txt'
            inInter = '../supportFiles/exampleRun/userOutput/interactionsTable.txt'


        else:
            inNodes = params['text25']
            inLinks = params['text26']
            inInter = params['text27']


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

        if params['dropdown2'] == 'Current':
            head.append(script)
        else:
            webbrowser.open('http://localhost:8080/widget7_out',new=1)

        return head
        
        
        
        
         
        
if __name__ == '__main__':
    app = Widget7()
    app.launch()
