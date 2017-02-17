import cherrypy
#cherrypy.config.update({"response.timeout":1000000,'log.access_file': '../supportFiles/logs/logAccess_file.txt','log.error_file': '../supportFiles/logs/logError_file.txt','log.screen':True})

def getListOfModels(comFolder):
    '''
    This function creates a list with all the community models that will be used in the analysis. It creates this list by listing the metabolic models in SBML format present in the user specified folder that contains the community models.

    :param comFolder: path to the folder that contains the community metabolic models.
    :return listOfModels: list object containing the filenames for all the models that will be analysed in the function calculateGR
    '''

    import os
    cherrypy.log('We will first get the full list of community models from the %s folder' %comFolder)
    
    path = comFolder
    listOfFiles = os.listdir(path)

    listOfModels = []
    
    for file in listOfFiles:
        if file.endswith('.sbml'):
            pathToFile = path + file
            listOfModels.append(pathToFile)

    cherrypy.log('There are %s community models what will be analyzed.'%listOfModels)

    return listOfModels


def calculateGR(diet,outputGRs, comFolder):
    '''
    In this function we use cobrapy to calculate the growth rates of the two species that make up the two species community metabolic models under particular metabolite availability conditions. We start by loading the community model (full model) into 3 distinct Model objects with cobrapy. We then change the fluxes of the exchange reactions of the external model so they have lower bounds corresponding to whichever 'Diet' condition the user specifies. We then run a flux balance analysis on the full model, optimizing the biomass reactions of the two species that make up the community at the same time. It then remove all reactions whose IDs start with modelA from the model in modelMinusA, thus leaving only the reactions from modelB and from the external compartment. It then runs a FBA on it, maximizing the biomass reaction for the model with the tag modelB. It then does the samething but for reactions tagged with modelB on modelMinusB. The optimal flux values for the biomass reactions of each species resulting from optimization in the full model and in each model containing only one species, which correspond to predicted growth rates, are then exported to a table in the tab-delimited text formal to a folder chosen by the user.

    :param diet: the metabolite availability conditions. Default on MMinte is complete, but the user can choose another value ('Variant1 through 10')
    :param outputGRs: path to the file that contains the table with the predicted growth rates of the species in a community and in isolation
    :param comFolder: path to the folder containing all the two-species community metabolic models.
    :return outputGRs: table with growth rate information for each of the species belonging to a two-species community metabolic model in the presence and absence of another species.
    '''
    
    import cobra
    
    cherrypy.log('We will now calculate the growth rates of the two species in a community model in the presence and absence of the other species')
    growthRatesFile = open(outputGRs,'a')
    
    
    print>>growthRatesFile, 'ModelName', '\t', 'ObjFuntionSpeciesA', '\t', 'ObjFunctionSpeceisB', '\t', 'GRSpeciesAFull','\t', 'GRSpeciesBFull','\t','GRASolo','\t','GRBSolo'
    

    # Create a list of all the models that will be analysed
    allModels = getListOfModels(comFolder)


    for item in range(len(allModels)):
        
        '''
        @summary: load the model, all versions that will be manipulated in the analysis.
        '''

        # Import the models with cobrapy
        modelFull = cobra.io.read_sbml_model(allModels[item])
        modelMinusA = cobra.io.read_sbml_model(allModels[item])
        modelMinusB = cobra.io.read_sbml_model(allModels[item])

        cherrypy.log('We successfully loaded the file %s into three different Model objects with ids, %s, %s, and %s. They should all have the same id.'%(allModels[item],modelFull.id,modelMinusA.id,modelMinusB.id))
        


        # Determine what the objective function is. It should be composed of two reactions, the biomass reactions for each of the species that compose the model. Store the biomass reactions in a new variable to be used later.
        ObjKeys = modelFull.objective.keys()
        idObjKeys = ObjKeys[0].id, ObjKeys[1].id

        cherrypy.log('The objective function of the full model, %s, contains the objective functions of the two models that make it up. They are %s.'%(allModels[item], idObjKeys))
        

        
        # Open the metabolite conditions file ('Diet')
        dietValues = open('../supportFiles/Diets/Diets.txt','r')
        dietValues.readline()
    
        # Default 'Diet' for MMinte is Complete. After choosing the 'Diet' change the lower bounds for the exchange reactions of the external compartment.

        cherrypy.log('The diet chosen for this particular run of the functions was %s' %diet)

        for line in dietValues:
            try:
                new_line = line.rstrip('\n').split('\t')
                if diet == 'Complete':
                    modelFull.reactions.get_by_id(new_line[0]).lower_bound = float(new_line[2])
                    modelMinusA.reactions.get_by_id(new_line[0]).lower_bound = float(new_line[2])
                    modelMinusB.reactions.get_by_id(new_line[0]).lower_bound = float(new_line[2])
                
                elif diet == 'Variant1':
                    modelFull.reactions.get_by_id(new_line[0]).lower_bound = float(new_line[3])
                    modelMinusA.reactions.get_by_id(new_line[0]).lower_bound = float(new_line[3])
                    modelMinusB.reactions.get_by_id(new_line[0]).lower_bound = float(new_line[3])
            
                elif diet == 'Variant2':
                    modelFull.reactions.get_by_id(new_line[0]).lower_bound = float(new_line[4])
                    modelMinusA.reactions.get_by_id(new_line[0]).lower_bound = float(new_line[4])
                    modelMinusB.reactions.get_by_id(new_line[0]).lower_bound = float(new_line[4])

                elif diet == 'Variant3':
                    modelFull.reactions.get_by_id(new_line[0]).lower_bound = float(new_line[5])
                    modelMinusA.reactions.get_by_id(new_line[0]).lower_bound = float(new_line[5])
                    modelMinusB.reactions.get_by_id(new_line[0]).lower_bound = float(new_line[5])

                elif diet == 'Variant4':
                    modelFull.reactions.get_by_id(new_line[0]).lower_bound = float(new_line[6])
                    modelMinusA.reactions.get_by_id(new_line[0]).lower_bound = float(new_line[6])
                    modelMinusB.reactions.get_by_id(new_line[0]).lower_bound = float(new_line[6])

                elif diet == 'Variant5':
                    modelFull.reactions.get_by_id(new_line[0]).lower_bound = float(new_line[7])
                    modelMinusA.reactions.get_by_id(new_line[0]).lower_bound = float(new_line[7])
                    modelMinusB.reactions.get_by_id(new_line[0]).lower_bound = float(new_line[7])

                elif diet == 'Variant6':
                    modelFull.reactions.get_by_id(new_line[0]).lower_bound = float(new_line[8])
                    modelMinusA.reactions.get_by_id(new_line[0]).lower_bound = float(new_line[8])
                    modelMinusB.reactions.get_by_id(new_line[0]).lower_bound = float(new_line[8])

                elif diet == 'Variant7':
                    modelFull.reactions.get_by_id(new_line[0]).lower_bound = float(new_line[9])
                    modelMinusA.reactions.get_by_id(new_line[0]).lower_bound = float(new_line[9])
                    modelMinusB.reactions.get_by_id(new_line[0]).lower_bound = float(new_line[9])

                elif diet == 'Variant8':
                    modelFull.reactions.get_by_id(new_line[0]).lower_bound = float(new_line[10])
                    modelMinusA.reactions.get_by_id(new_line[0]).lower_bound = float(new_line[10])
                    modelMinusB.reactions.get_by_id(new_line[0]).lower_bound = float(new_line[10])

                elif diet == 'Variant9':
                    modelFull.reactions.get_by_id(new_line[0]).lower_bound = float(new_line[11])
                    modelMinusA.reactions.get_by_id(new_line[0]).lower_bound = float(new_line[11])
                    modelMinusB.reactions.get_by_id(new_line[0]).lower_bound = float(new_line[11])

                elif diet == 'Variant10':
                    modelFull.reactions.get_by_id(new_line[0]).lower_bound = float(new_line[12])
                    modelMinusA.reactions.get_by_id(new_line[0]).lower_bound = float(new_line[12])
                    modelMinusB.reactions.get_by_id(new_line[0]).lower_bound = float(new_line[12])
                

                
            except:
                continue
        
        dietValues.close()

        cherrypy.log('We finished changing the lower bounds for the fluxes of the exchange reactions in the models to better fit the availability of metabolites for the microbial communities we are simulating the growth of. ')
        

        # Run FBA on Full model
        modelFull.optimize()

        cherrypy.log('We finished running the FBA on the full model. The status of the solution is %s and the value of the solution found is %f'%(modelFull.solution.status,modelFull.solution.f))

        # Find which reactions are tagged as being from modelA, store them in a list, then create the modelMinusA, that is, remove all reactions that are part of one of the species in the model.
        # Run FBA on that reduced model.

        cherrypy.log('We are now going to remove all reactions that are tagged as being of species A from the model.')

        listSilentItemsA = []
        
        for item in modelMinusA.reactions:
            item = str(item)
            if item.startswith('modelA_'):
                listSilentItemsA.append(item)

        cherrypy.log('We found %d reactions tagged as being of species A'%len(listSilentItemsA))


        for j in listSilentItemsA:

            rxn = j.strip()
            deadRxnA = modelMinusA.reactions.get_by_id(rxn)
            deadRxnA.remove_from_model()

        cherrypy.log('We finished removing all reactions from the model. The model now has %s reactions and the reaction on the objective function in %s'%(len(modelMinusA.reactions),modelMinusA.objective))
        
        modelMinusA.optimize()

        cherrypy.log('We finished running the FBA on the model without reactions of species A. The status of the solution is %s and the value of the solution found is %f'%(modelMinusA.solution.status,modelMinusA.solution.f))


        # Find which reactions are tagged as being from modelB, store them in a list, then create the modelMinusB, that is, remove all reactions that are part of one of the species in the model.
        # Run FBA on that reduced model.

        cherrypy.log('We are now going to remove all reactions that are tagged as being of species B from the model.')

        listSilentItemsB = []
        
        for item in modelMinusB.reactions:
            item = str(item)
            if item.startswith('modelB_'):
                listSilentItemsB.append(item)

        cherrypy.log('We found %d reactions tagged as being of species B'%len(listSilentItemsB))
        for j in listSilentItemsB:
            rxn = j.strip()
            deadRxnB = modelMinusB.reactions.get_by_id(rxn)
            deadRxnB.remove_from_model()

        cherrypy.log('We finished removing all reactions from the model. The model now has %s reactions and the reaction on the objective function in %s'%(len(modelMinusB.reactions),modelMinusB.objective))
        
        modelMinusB.optimize()

        cherrypy.log('We finished running the FBA on the model without reactions of species A. The status of the solution is %s and the value of the solution found is %f'%(modelMinusB.solution.status,modelMinusB.solution.f))


        # Get the x_dict values (fluxes) for the reactions listed under idObjKeys for all three models.
        # Output them to a file with a table that has the information about the model, the species ID in the model, and the growth rates of each species in the full model and in isolation.


        ObjA = []
        ObjB = []
        
        if idObjKeys[0].startswith('modelA'):
            ObjA = idObjKeys[0]
        else:
            ObjB = idObjKeys[0]
            
        
        if idObjKeys[1].startswith('modelB'):
            ObjB = idObjKeys[1]
        else:
            ObjA = idObjKeys[1]

        cherrypy.log('We matched the reactions in the objective function to the model they came from. %s was originally from modelA and %s was originally from mobelB' %(ObjA,ObjB))
        
        grAfull = modelFull.solution.x_dict[ObjA]
        grBfull = modelFull.solution.x_dict[ObjB]

        cherrypy.log("We are going to create a table with the information about the growth of A and B alone and in the presence of B and A respectively.")
        
        if ObjA in modelMinusA.solution.x_dict:
            grAMinusA = modelMinusA.solution.x_dict[ObjA]
        else:
            grAMinusA = 'Solo'
        
        
        if ObjB in modelMinusA.solution.x_dict:
            grBMinusA = modelMinusA.solution.x_dict[ObjB]
        else:
            grBMinusA = 'Solo'
        
        
        if ObjA in modelMinusB.solution.x_dict:
            grAMinusB = modelMinusB.solution.x_dict[ObjA]
        else:
            grAMinusB = 'Solo'
        
        
        if ObjB in modelMinusB.solution.x_dict:
            grBMinusB = modelMinusB.solution.x_dict[ObjB]
        else:
            grBMinusB = 'Solo'

        if grAMinusA != 'Solo' or grBMinusB != 'Solo':
            cherrypy.log('There is a problem with the attribution of growth rate values to their respective species in model %s .'%modelFull.id)

        
        modelID = modelFull.id
        organisms = modelID.split('X')
        


        print>> growthRatesFile, modelID, '\t', organisms[0], '\t', organisms[1], '\t', grAfull,'\t', grBfull,'\t',grAMinusB,'\t',grBMinusA

    cherrypy.log('We finished calculating the growth rates of the species in isolation and when in the presence of another species and dumped the information to the file: %s' %growthRatesFile)

    growthRatesFile.close()



