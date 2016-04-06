from spyre import server
import io
import os



import cherrypy
class custom_root(server.Root):
    @cherrypy.expose
    def image1(self, **args):
        import io
        buffer = io.BytesIO()
        ROOT_DIR = os.path.dirname(os.path.realpath('static/images/3485812-14.jpg'))
        f = open(ROOT_DIR+'/3485812-14.jpg','rb' )
        buffer.write(f.read())
        f.close()
        return buffer.getvalue()
    @cherrypy.expose
    def image2(self, **args):
        import io
        buffer = io.BytesIO()
        ROOT_DIR = os.path.dirname(os.path.realpath('static/images/flow.jpg'))
        f = open(ROOT_DIR+'/flow.jpg','rb' )
        buffer.write(f.read())
        f.close()
        return buffer.getvalue()

server.Root=custom_root

        
class Index(server.App):
    title='Intro'
    outputs = [{"output_type": "html",
                "output_id": "Index",
                "on_page_load": True}]
    
    def getCustomCSS(self):
        ROOT_DIR = os.path.dirname(os.path.realpath('static/custom_styleMMinte.css'))
        with open(ROOT_DIR + '/custom_styleMMinte.css') as style:
            return style.read()+'''\n .left-panel{display: none;}.right-panel{width:100%;margin:px;background: white;padding: 0px}'''
    
    
    def getHTML(self, params):

        return '''
<!-- Index page for MMinte app -->

    <head>
        <meta name="description" content="MMinte - Microbial metabolic interaction">
        <META NAME="ROBOTS" CONTENT="INDEX, FOLLOW">
    </head>
    
    <style>
        
        
        body {background-color: #f4f4f4;
                padding: 2em;
                margin-left:1em;
                margin-right:1em;
                margin-top:1em;
                margin-bottom:1em;
                border-radius: 10px;
        }
        
        
        
        h1.text {
            color: #00961E;
            text-align: center;
            font-family: "Arial";
            font-size: 3em;
            padding:0em;
        }
       
        p {color: black;
            text-align: justify;
            font-family: "Arial";
            font-size: 1.5em;
            line-height:1.2;
            text-indent: 2em;
            padding:1em;
        }
        
        h2 {
            text-indent: 2em;
            font-family: "Arial";
        }
        
        ul{
            text-align: justify;
            list-style-type:none;
            font-family: "Arial";
            font-size: 1.2em;
            line-height:1.3;
        }
        
        p.contact{font-size: 1.5em;
                font-family: "Arial";
                text-align: center;
                text-indent: 0em;
        }
                
        img.displayed {
                        width:65em;
                        height:27em;
                        display: block;
                        margin-left: auto;
                        margin-right: auto
        }
        
        img.flow{
                    width: 30em;
                    height: 45em;
                    float:right;
                    margin: 0 10px 10px 20px;
                    border: 2px solid black;
                    }
        
        a:link {color:black;
                text-decoration: none;
                }

        a:visited {text-decoration: none;
                }

        a:hover {text-decoration: underline;
                }

        a:active {text-decoration: underline;
                }    
    </style>
    

    <body>
    
   
    <img class="displayed" src='/image1' alt="MMinte logo" >
    
     <div>
    
    <h1 class="text">Welcome to MMinte!</h1>
    
    <h2>
        The least you need to know:
    </h2>
    <p>
        The microbiome is an expanding field of research in the biological sciences. Its integrative approaches have mostly included 16S rDNA surveys. These surveys have been used to generate associative community network topologies, but do not assess the mechanistic basis of these associations. Here, we present <strong><font color=#00961E>MMinte</strong></font> a tool for assessing the microbial metabolic interactions within a microbiome network.  With <strong><font color=#00961E>MMinte</strong></font>, users need only provide 
        a table containing pairs of operational taxonomic units (OTUs) that will be the focus of the analysis and representative sequences for those OTUs. 
        <strong><font color=#00961E>MMinte</strong></font> will then perform a series of sequential tasks to assess the kind of ecological interactions that are potentially 
        occurring between each two members of the community. The final output is a network diagram representing these interactions.
            
        <strong><font color=#00961E>MMinte</strong></font> is divided into 7 widgets with specific functions that may be used individually or sequentially. This modularity allows the 
        user to have better control of the workflow.
    </p>
    
    <h2>    
        The full description:
    </h2>
    
    <p>
        <strong><font color=#00961E>MMinte</strong></font> (pronounced /`minti/) is an integrated pipeline that allows users to explore the different kinds of pairwise interactions occurring 
        between members of a microbial community under different nutritional conditions. These interactions are predicted for the taxonomic units 
        of interest from as little information as the 16S dRNA sequences commonly obtained in studies describing the species membership of microbial 
        communities. Our application is composed of seven widgets that run sequentially, with each widget utilizing as the input file created in the
        previous widget as the default file for analysis. While <strong><font color=#00961E>MMinte</strong></font> may be run as a streamlined pipeline, due to its 
        compartmentalized nature, the user is given the ability to better control the full analysis. The user may choose to start the application 
        at any of the seven widgets, as long as the data provided has the adequate structure. The user also has access to the output files of each 
        widget (stored in the folder /userOutput). This allows the user to verify the quality of the data produced at each step of the analysis, 
        as well as explore it with alternative tools. 
    </p>
    
    <p>
        The widgets that make up <strong><font color=#00961E>MMinte</strong></font>, and the particular analysis they perform on the particular input files they take (see examples on folder 
        \supportFile\examples), are the following:
        
        <ul><img class="flow" src="/image2" alt="MMinte flow" >
        
        
 
            <li>
        <ins>Widget 1</ins> - Using information about pairs of operational taxonomic units (OTUs) that are associated to some degree and a list of 16S rDNA sequences for the OTUs in a particular community, a file is created containing only the sequences for representative OTUs significant to the analyses.
 
            </li>
            
            <br>
            
            <li>
        <ins>Widget 2</ins> - The representative OTUs are identified and assigned a genome ID using BLAST and a local database containing the 16S rDNA sequences of species with whole genome sequences.

            </li>
            
            <br>
            
            <li>
        <ins>Widget 3</ins> - Metabolic models for each genome ID are reconstructed and gap-filled using ModelSEED and downloaded to the user's local machine.

            </li>

            <br>
            
            <li>
        <ins>Widget 4</ins> - Metabolic models of 2- species communities are created using COBRA Toolbox for the python computational framework (COBRApy).
            </li>
            
            <br>
            
            <li>
        <ins>Widget 5</ins> - Under defined nutritional conditions, the growth rates of each species in isolation and when in the presence of another species in the community are estimated.
            </li>
        
            <br>
            
            <li>
        <ins>Widget 6</ins> - The kinds of interactions occurring between the pairs of species on the nutritional conditions defined in Widget 5 are predicted. The interactions are either positive (commensalism, mutualism) or negative (parasitism, amensalism, competition).
            </li>
        
            <br>
            
            <li>
        <ins>Widget 7</ins> - A network is plotted with D3.js using the initial information of associations between the pairs of OTUs provided by the used, and the kinds of interactions predicted to be occurring.
            </li>
    <br>
    
    
    </ul>
        
        
    </p>
    <br>
    <br>
    <br>
    <br>
    <br>
    
    <p style="text-align:center">
        <strong><font color=#00961E>MMinte</strong></font> was developed by scientists and developers at the Center for Individualized Medicine at the Mayo Clinic and Harvard Medical School. 
    </p>

	<p style="text-align:center">
        Please note that <strong><font color=#00961E>MMinte</strong></font> is still being actively developed. If you want us to let you know of updates, just shoot us an email. Also, a manuscript has been submitted for publication in a scientific journal, so if you give us your contact, we can let you know how that goes!
    </p>
    
    
    <h2 style="text-align:center"><ins>Contact and Suggestions:</ins></h2>

    <p class="contact">Mail <a href="mailto:microbialmetabolicinteractions@gmail.com"><strong><font color=#00961E>MMinte</strong></font>'s awesome team!</a></p>
    
    </div>
    
    </body>
    '''


import cherrypy 

if __name__ == '__main__':
    app = Index()
    app.launch()