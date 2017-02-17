import cherrypy
import cobra
import itertools
import os
#cherrypy.config.update({"response.timeout":1000000,'log.access_file': '../supportFiles/logs/logAccess_file.txt','log.error_file': '../supportFiles/logs/logError_file.txt','log.screen':True})

'''
    The set of functions in this widget allow the automatic creation of two-species community metabolic models, either from user defined list of pairs of species or from a list created automatically from the models available in the folder with individuals species metabolic models.

'''

def createAllPairs(modelFolder,outputFolder = '../tempFiles/pairsList.txt'):

    '''
    This function lists the files for species metabolic models that exist in the folder specified in modelFolder and creates a list with all possible pairwise combinations of species models. This function is only called if the user doesn't provide a file with the list of species to pair or the files required for the function createSubsetPairs (below).

    :param modelFolder: path to the folder containing all the individual species metabolic models in SBML format.
    :return pairsListFile: file with a list of pairs of species that will make up each of the two-species community metabolic models. This file is created and stored in the tempFiles folder.
    '''


    cherrypy.log('Will start running function to create a list of all possible pairs of 2-species combination from the models in the folder %s' %modelFolder)

    listFiles = []
    for file in os.listdir(modelFolder):
        if file.endswith('.sbml'):
            id = file[:-5]
            listFiles.append(id)

    cherrypy.log('There are %d files in the folder %s .' %(len(listFiles),modelFolder))


    pairsListFile = open(outputFolder,'w')

    print>>pairsListFile, 'OtuAGenomeID', 'OtuBGenomeID'

    counter = 0

    for c in itertools.combinations(listFiles,2):
        print>>pairsListFile, c[0], c[1]
        counter += 1

    pairsListFile.close()

    cherrypy.log('Finished creating a file (%s) with all the possible pairwise combinations of species. There are %d pairs of species IDs in this file' %(pairsListFile, counter))


def createSubsetPairs(similFilePath,corrsFilePath):
    '''
    This function creates a list of pairs of models that will make up each of the two-species community metabolic models. This list is created two files. One is a file with the association values between pairs of OTUs (same file used in Widget 1). This file contains 3 columns. Columns 1 and 2 are lists of identifiers of OTUs from the microbiome study the user is interested in exploring. The third column has some value of associaltion between each pair of OTUs. The other is a file with information about the percent similarity between the sequences of the queried OTUs and the matching sequences from the local database. It contains four columns. The first column is the row number this will be used in the plotting of the interaction network in Widget 7. The second row lists the identifiers of the OTUs whose 16S seqeunces were blasted against the local 16S database. The third column lists the ID of he genome whose species the sequence of the query OTU matched. The fourth column lists the percent similarity values bwteen the queried sequence and the match in the database.

    :param similFilePath: file containing the information about the percent similarity between queried OTUs and matching database sequences.
    :param corrsFilePath: file with the values of association between pairs of OTUs
    :return: pairsListFile: file with a list of pairs of species that will make up each of the two-species community metabolic models. This file is created and stored in the tempFiles folder.
    '''


    cherrypy.log('Will start running function to create a list of all pairs of 2-species combinations based on the initial correlation file from the user. For this we will use the correlation file used in widget 1 (%s) and the percent similarity file created in widget 2 (%s)' %(corrsFilePath,similFilePath))

    similFile = open(similFilePath,'r')
    similTable = []
    for i in similFile:
        i = i.rstrip()
        i = i.split()
        similTable.append(i)

    cherrypy.log('The number of lines in the table with the percent similarity between OTUs and a particular species is %d'%len(similTable))



    corrsFile = open(corrsFilePath, 'r')
    corrsTable = []
    for i in corrsFile:
        i = i.rstrip()
        i = i.split()
        corrsTable.append(i)

    cherrypy.log('The number of lines in the table with the correlations between OTUs and a particular species is %s '%len(corrsTable))

    ############

    tempTableA = []
    first_line = 'otuA','otuB','speciesA'
    tempTableA.append(list(first_line))

    for i in corrsTable:
        for j in similTable:
            if i[0] == j[1]:
                new_line = i[0],i[1],j[2]
                tempTableA.append(list(new_line))
            else:
                continue

    cherrypy.log('Finished creating the first temporary table.')


    tempTableB = []


    for i in tempTableA:
        for j in similTable:
            if i[1] == j[1]:
                new_line = i[2] + 'X' + j[2]
                tempTableB.append(new_line)
            else:
                continue

    cherrypy.log('Finished creating the second temporary table.')

    tempTableC = list(set(tempTableB))

    cherrypy.log('There are %d unique combinations of two species that will be used to create the community models.'%(len(tempTableC)))

    pairsListFile = open('../tempFiles/pairsList.txt','w')

    print>>pairsListFile,'speciesA','speciesB'

    for item in tempTableC:
        line = item.split('X')
        print>>pairsListFile,line[0], line[1]

    pairsListFile.close()
    cherrypy.log('We finished exporting the information about all pairwise combinations to the file %s'%pairsListFile)
    pass






def totalEXRxns(modelA,modelB): 
    '''
    This function creates a list object with the id (Reaction.id method from cobrapy) for all the unique exchange reactions found in both models listed (modelA, modelB). These exchange reactions are then differentiated from the reactions from models A and B by an additional tag in the end of the reaction id ([u])

    :param modelA: cobrapy Model object
    :param modelB: cobrapy Model object
    :return EX_finalRxns: list with the ids of all the unique exchange reactions from modelA and modelB.
    '''

    cherrypy.log('Started function totalEXRxns. Working on %s as modelA and %s as modelB' %(modelA,modelB))


    # List all the exchange reactions in modelA
    EX_rxnsA = set()
    for i in range(len(modelA.reactions)):
        rxnsA = str(modelA.reactions[i])
        if 'EX_' in rxnsA:
            EX_rxnsA.add(rxnsA)
    

    cherrypy.log('Finished finding all exchange reactions in modelA. There are %d of them' %(len(EX_rxnsA)))


    # List all the exchange reactions in modelB
    EX_rxnsB = set()
    
    for j in range(len(modelB.reactions)):
        rxnsB = str(modelB.reactions[j])
        if 'EX_' in rxnsB:
            EX_rxnsB.add(rxnsB)


    cherrypy.log('Finished finding all exchange reactions in modelB. There are %d of them' %(len(EX_rxnsB)))


    # List all the different exchange reactions that are present in models A and B. They will have some that overlap.
    EX_total =  list(EX_rxnsA | EX_rxnsB)


    cherrypy.log('Finished creating a list with all the exchange reactions existing in the two models. There are %d of them' %(len(EX_total)))


    # Create a list with all the Exchange reactions and assign them a new identifier. These will be the exchange reactions that will make up the external compartment that is common to both bacterial species.
    EX_finalRxns = []
    for each in range(len(EX_total)):
        rxn = EX_total[each] + '[u]'
        EX_finalRxns.append(rxn)


    cherrypy.log('Finished adding the tag [u] to the end of the exchange reactions')

    return EX_finalRxns


def createEXmodel(EXreactions): 
    '''
    This function takes the list of exchange reactions created using the function totalEXRxns and creates a Model object using cobrapy composed of those reactions with the upper bound flux values of 1000, lower bound flux values of -1000, and objective coefficient of 0, and one metabolite as being uptaken by the reaction (stoichiometric coefficient of -1). This is a model composed solely of exchange reactions and it's the model for the extra compartment created for the full community model

    :param EXreactions: list of reactions that are the output of the function totalEXRxns (above)
    :return exchange_model: cobrapy Model object for the compartment that will serve as an extra compartment in the full community model.
    '''


    cherrypy.log("Started the function that creates the exchange reactions for the community model")

    exchange_model = cobra.Model('Model with the exchange reactions only')

    cherrypy.log("Created the base exchange model object")
    
    for i in EXreactions: 
        new_i = str(i)
        new_i = new_i[3:]
        new_met = cobra.Metabolite(new_i)
        
        rxn = cobra.Reaction(i)
        rxn.lower_bound = -1000.000
        rxn.upper_bound = 1000.000
        rxn.objective_coefficient = 0.000
        rxn.add_metabolites({new_met:-1.0}) 
        
        exchange_model.add_reaction(rxn)


    cherrypy.log('Finished adding all exchange reactions in exchange model object. There are %d of them' %(len(exchange_model.reactions)))

    return exchange_model 


def createReverseEXmodel(EXreactions): 
    '''
    This function takes the list of exchange reactions created using the function totalEXRxns and creates a Model object using cobrapy composed of those reactions with the upper bound flux values of 1000, lower bound flux values of -1000, and objective coefficient of 0, and one metabolite as being produced by the reaction (stoichiometric coefficient of 1). This is a model composed solely of exchange reactions. The metabolite information for these reactions will be used to update the metabolites of the exchange reactions for models A and B.

    :param EXreactions: list of reactions that are the output of the function totalEXRxns (above)
    :return exchange_modelRev: cobrapy Model object containing only exchange reactions with the production of their respective metabolites
    '''

    cherrypy.log("Started the function that creates the reverse exchange reactions for the community model")

    exchange_modelRev = cobra.Model('Model with the exchange reactions only with reversed stoi coefficient')

    cherrypy.log("Created the base reverse exchange model object")

    for i in EXreactions: 
        new_i = str(i)
        new_i = new_i[3:]
        new_met = cobra.Metabolite(new_i)
        
        rxn = cobra.Reaction(i)
        rxn.lower_bound = -1000.000
        rxn.upper_bound = 1000.000
        rxn.objective_coefficient = 0.000
        rxn.add_metabolites({new_met:1.0})
        
        exchange_modelRev.add_reaction(rxn)

    cherrypy.log('Finished adding all exchange reactions in reverse exchange model object. There are %d of them' %(len(exchange_modelRev.reactions)))

    return exchange_modelRev



def addEXMets2SpeciesEX(reverseEXmodel,speciesModel):
    '''
    This function takes the model with exchange reactions where the metabolite is produced (output from function createReverseEXmodel) and a species model, and adds the metabolite from the reverse model to the exhange reactions of the species model. For instance:

    Reaction :  modelB_EX_cpd11588_e0 got the cpd11588_e0[u] added.
                'model_B_cpd11588_e0 <=> cpd11588_e0[u]'

    This way, when a compound is exported to the extracellular environment, it is automatically transformed into a form that is common to all members in the community.

    :param reverseEXmodel: cobrapy Model object containing only exchange reactions with the production of their respective metabolites
    :param speciesModel: Model object of a particular species.
    :return speciesModel: Model object of a particular species with updated exchange reactions are updated.
    '''

    cherrypy.log('Started function to add metabolites to the exchange reactions of the reverse exchange model') #not right

    for j in range(len(reverseEXmodel.reactions)):
        exRxn = str(reverseEXmodel.reactions[j])
        
        for i in range(len(speciesModel.reactions)):
            rxn = str(speciesModel.reactions[i])
            if rxn in exRxn:
                new_met = reverseEXmodel.reactions[j].metabolites 
                speciesModel.reactions[i].add_metabolites(new_met)
                speciesModel.reactions[i].lower_bound = -1000.000
                speciesModel.reactions[i].upper_bound = 1000.000

    cherrypy.log('Finished adding metabolites to the exchange reactions of the reverse exchange model')
    return speciesModel       
               
   
def replaceRxns(model,modelID):    
    '''
    This function adds the tag specified in the parameter modelID to the beginning of the reaction IDs for a particular Model object. We are doing this so that we know which reactions come from one species or the other. This is the same as assigning each species to a different compartment. This is important because the two species have common reactions and metabolites, but are not sharing these metabolites in their biology, since the cells are closed compartments. They only share the metabolites that are transported in and out of the cell, hence the creation of an extra external compartment.

    :param model: Model object containing the metabolic model of a particular species
    :param modelID: Tag to add to the beginning of the reaction IDs of the model.
    :return model: same model but with updated reactions IDs
    '''


    cherrypy.log('Started function to replace the reaction IDs in the species models')

    
    for i in range(len(model.reactions)):
        old_rxns = str(model.reactions[i])
        new_rxns = 'model' + modelID + '_' + old_rxns
        model.reactions[i].id = new_rxns

    cherrypy.log('Finished changing the reaction IDs in the species models')

def replaceMets(model,modelID):
    '''
    This function adds the tag specified in the parameter modelID to the beginning of the metabolite IDs for a particular Model object. We are doing this so that we know which metabolites come from one species or the other. This is the same as assigning each species to a different compartment. This is important because the two species have common reactions and metabolites, but are not sharing these metabolites in their biology, since the cells are closed compartments. They only share the metabolites that are transported in and out of the cell, hence the creation of an extra external compartment.

    :param model: Model object containing the metabolic model of a particular species
    :param modelID: Tag to add to the beginning of the metabolite IDs of the model.
    :return model: same model but with updated metabolite IDs
    '''

    cherrypy.log('Started function to replace the metabolite IDs in the species models')

    
    for i in range(len(model.metabolites)):
        old_mets = str(model.metabolites[i])
        new_mets = 'model_' + modelID + '_' + old_mets
        
        model.metabolites[i].id = new_mets

    cherrypy.log('Finished changing the metabolite IDs in the species models')



def createCommunityModel(modelFileA, modelFileB, comFolder):
    '''
    This function takes advantage of the outputs of all the functions defined previously to actually piece together the individual species models and the extra compartment model.


    :param modelFileA: path to the metabolic model of species A in SBML format
    :param modelFileB: path to the metabolic model of species B in SBML format
    :param comFolder:  path to the folder where the metabolic models of the two-species communities will be stored.

    :return two-species community model: in SBML format exported to the folder designated by the user (comFolder) to store these models
    '''
    
    cherrypy.log('Started function to create community models. ModelFileA is %s, ModelFileB is %s, and the folder where we are going to put the files in is %s' %(modelFileA, modelFileB, comFolder))

    
    #import the model file into the Model object model1 using cobrapy
    try:
        if modelFileA.endswith('.mat'):
            cherrypy.log('The extension is .mat .This is modelfileA %s' %modelFileA)
            model1 = cobra.io.load_matlab_model(modelFileA)
        elif modelFileA.endswith('.xml') or modelFileA.endswith('.sbml'):
            cherrypy.log('The extension is .xml or .sbml .This is modelfileA %s' %modelFileA)
            model1 = cobra.io.read_sbml_model(modelFileA)
        elif modelFileA.endswith('.json'):
            cherrypy.log('The extension is .json . This is modelfileA %s' %modelFileA)
            model1 = cobra.io.load_json_model(modelFileA)
        else:
            cherrypy.log('We were not able to find a model. This is modelfileA %s' %modelFileA)
            print "not able to find model %s" %modelFileA
    except Exception as e:
        print e

    cherrypy.log('%s loaded successfully' %model1.id)

    #import the model file into the Model object model2 using cobrapy
    if modelFileB.endswith('.mat'):
        cherrypy.log('The extension is .mat .This is modelfileB %s' %modelFileB)
        model2 = cobra.io.load_matlab_model(modelFileB)
    elif modelFileB.endswith('.xml') or modelFileB.endswith('.sbml'):
        cherrypy.log('The extension is .xml or .sbml .This is modelfileB %s' %modelFileB)
        model2 = cobra.io.read_sbml_model(modelFileB)
    elif modelFileB.endswith('.json'):
        cherrypy.log('The extension is .json . This is modelfileB %s' %modelFileB)
        model2 = cobra.io.load_json_model(modelFileB)
    else:
        cherrypy.log('We were not able to find a model. This is modelfileB %s' %modelFileB)
        print "not able to find model %s" %modelFileB
        
    cherrypy.log('%s loaded successfully' %model2.id)


    # Create a communityID to identify the output files belonging to each 2-species community created
    communityID = model1.id+ 'X' + model2.id

    cherrypy.log('The communityID (reflected in the filename is %s .'%communityID)
    

    # Get all the reactions identified as exchange reactions in both models you're mixing and create a list with of exchange reactions. Then use this list to create what is called an exchange reaction model. This exchange reaction model will be the equivalent of an outside world model, or the lumen for instance, as in the models in Heinken and Thiele AEM 2015 paper. Later manipulation of this particular model will allow the user to choose the diet under which the communities are growing.
    cherrypy.log('Lets actually run the function that creates te model with the exchange reactions.')
    exModel = createEXmodel(totalEXRxns(model1, model2))

    

    # Create a model that has the fluxes of the exchange reactions reversed. This is because these reactions will will added specifically to each species, in the model. So we are extending the original species models to have more reactions so that each species can exchange metabolites with exchange reactions model. The exchange reactions models then becomes a comparment shared by all the other species in the community model. This is what will allow us to determine how the species interact when they have to share resources.
    cherrypy.log('Lets actually run the function that creates te model with the reverse exchange reactions.')
    revEXmodel = createReverseEXmodel(totalEXRxns(model1, model2))

    # Add a tag to the metabolite IDs of modelA and modelB.
    cherrypy.log('Lets actually run the function that replaces the metabolite IDs for modelA (%s) and modelB (%s).' %(model1,model2))
    replaceMets(model1,'A')
    replaceMets(model2,'B')

    # Add the metabolites of the external model to the exchange reactions of each species.
    cherrypy.log('Lets add the metabolites to the exchange reactions of the species models')
    new_m1 = addEXMets2SpeciesEX(revEXmodel,model1) 
    new_m2 = addEXMets2SpeciesEX(revEXmodel,model2) 


    # Add a tag to the reaction IDs of modelA and modelB.
    cherrypy.log('Lets replace the reaction IDs on the species models')
    replaceRxns(new_m1,'A')
    replaceRxns(new_m2,'B')

    cherrypy.log('Finished replacing the reaction IDs on the species models')
    
    

    # Actually create the community model. All previous steps were changing the models that will be put together in the community so that the reactions and metabolites for each organism can still be distinguished and there is proper compartmentalization of reactions and metabolites. Because you can't really create a model from the sum of other 2, I just created a new model (mix) that is exactly model1. The alternative would have been to create an empty model, then add the reactions and metabolites of model1, model2, and exModel.
    cherrypy.log('Now, after we prepared every piece, we are going to put it all together in a community model')
    mix = new_m1
    mix.id = communityID
    mix.add_reactions(new_m2.reactions)
    mix.add_metabolites(new_m2.metabolites)
    mix.add_reactions(exModel.reactions)
    mix.add_metabolites(exModel.metabolites)

    cherrypy.log('A community model with the id %s was created. It has %d reactions and %d metabolites'%(mix.id, len(mix.reactions),len(mix.metabolites)))

    # Export the newly created community model to its folder. The models should then be ready to be further analyzed on Widget 5
    cobra.io.write_sbml_model(mix, "%s/community%s.sbml" %(comFolder,communityID))

    cherrypy.log('The model has been exported to the %s folder'%comFolder)


    

def allPairComModels(listOfPairs,modelFolder,comFolder):
    '''
    This function goes through a list with the models that should be paired together to form a community and creates the corresponding two-species community metabolic model using the function createCommunityModel

    :param listOfPairs: file with pairs of species that will make up each two-species community metabolic model.
    :param modelFolder: path to the folder containing the metabolic models of individual species in a SBML format
    :param comFolder: path to the folder that will store the two-species community metabolic models.
    :return set of two-species community metabolic models
    '''
    import os

    cherrypy.log('We are going to run the createCommunityModel script for all pairs of models in the %s file' %listOfPairs)

    # Check if the directory where two-species community models will be stored exists. If not, create it.
    if not os.path.exists(comFolder):
        os.makedirs(comFolder)
    
    pairsListFile = open(listOfPairs,'r')
    pairsListFile.readline()
    
    pairsList = []


    for i in pairsListFile:
        i = i.rstrip()
        i = i.replace("'","")
        i = i.split()
        pairsList.append(i)
    
    cherrypy.log('We created a list with the list of model pairs that will be put together. This list has %d pairs.' %(len(pairsList)))

    # Go down the list containing pairs of species and create a two-species community model.
    for i in range(len(pairsList)):
        modelA = modelFolder + '%s.sbml' %pairsList[i][0]
        modelA = str(modelA)
        cherrypy.log('The pair number %d will use file %s as modelA.' %(i,modelA))

        modelB = modelFolder + '%s.sbml' %pairsList[i][1]
        modelB =str(modelB)
        cherrypy.log('The pair number %d will use file %s as modelB.' %(i,modelB))
        try:
            createCommunityModel(modelA,modelB,comFolder)
        except Exception as e:
            print e
    
    cherrypy.log('We finished creating the models for all pairs in your list.')

    pairsListFile.close()
        
