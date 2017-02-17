import cherrypy
#cherrypy.config.update({"response.timeout":1000000,'log.access_file': '../supportFiles/logs/logAccess_file.txt', 'log.error_file': '../supportFiles/logs/logError_file.txt','log.screen':True})


def evaluateInteractions(inGRs, outInter):
    '''
    This function goes over the file with the growth rates of the species that make up a two-species community model and determines the kind of interaction occurring in between the two species. The types interactions are determined according to the paper by Heinken and Thiele 2015 AEM. These are determined based on the amplitude of change in growth rate of species in the presence and absence of another species in the community (>10% of change in growth of the particular species when in the presence of another species relative to the absence of another species indicates significant interaction), and the sign of the change (positive or negative). The information about the calculations of change and the type of interaction predicted in each community is added to the original table with the growth rates.

    :param inGRs: path to the file with the table listing the growth rates of the two species in a two-species community metabolic model in the presence and absence of another species in the community.
    :param outInter: path to the file that will contain the information contained in the file with growth rates, plus information regarding the the types of interactions predicted to be occurring in the community
    :return outInter: file with the interactions that are predicted to be occurring between species in a two-species community.
    '''

    cherrypy.log("We are in Widget 6.")
    cherrypy.log("We will use the information on the growth rates of the species in file %s to determine what kind of interaction is occurring between the organisms. We will output the table of interactions to %s. We will also count how many instances of each type of interaction are found" %(inGRs,outInter))

    grFile = open(inGRs, 'r')

    interactionsTableFile = open(outInter,'a')
    
    print>> interactionsTableFile, 'Model','\t','GenomeIDSpeciesA', '\t','GenomeIDSpeciesB','\t','GRSpeciesAFull','\t','GRSpeciesBFull','\t','GRASolo','\t','GRBSolo','\t','PercentChangeRawA','\t','PercentChangeRawB','\t', 'TypeOfInteraction'
    
    next(grFile)

    # We will count how many times each interaction is predicted to occur. This information is shown in the terminal window and in the logError file.
    countMutualism = 0
    countParasitism = 0
    countCommensalism = 0
    countCompetition = 0
    countAmensalism = 0
    countNeutralism = 0



    for item in grFile:
        
        item = item.replace("_",".")
        item = item.replace("A.","")
        item = item.replace(".model","")


        try:
            itemNew = item.split('\t')
            item = item.rstrip()

            # Calculation of the effect of the presence of a competing species in the growht rate of species A
            if float(itemNew[5]) != 0:
                percentChangeRawA = (float(itemNew[3])-float(itemNew[5]))/float(itemNew[5])
            else:
                percentChangeRawA = (float(itemNew[3])-float(itemNew[5]))/float(1e-25)


            # Calculation of the effect of the presence of a competing species in the growht rate of species B
            if float(itemNew[6]) != 0:
                percentChangeRawB = (float(itemNew[4])-float(itemNew[6]))/float(itemNew[6])
            else:
                percentChangeRawB = (float(itemNew[4])-float(itemNew[6]))/float(1e-25)
        
            # Assign a type of interaction to the community based on the percent change
            cherrypy.log('For this item, species A changed %f percent, and species B changed %f percent.'%(percentChangeRawA,percentChangeRawB))

            if percentChangeRawA > 0.1 and percentChangeRawB > 0.1:
                typeOfInteraction = 'Mutualism'
                countMutualism += 1

            elif percentChangeRawA > 0.1 and percentChangeRawB < -0.1:
                typeOfInteraction ='Parasitism'
                countParasitism += 1

            elif percentChangeRawA > 0.1 and percentChangeRawB > -0.1 and percentChangeRawB < 0.1:
                typeOfInteraction = 'Commensalism'
                countCommensalism += 1

            elif percentChangeRawA < -0.1 and percentChangeRawB > 0.1:
                typeOfInteraction = 'Parasitism'
                countParasitism += 1

            elif percentChangeRawA < -0.1 and percentChangeRawB < -0.1:
                typeOfInteraction = 'Competition'
                countCompetition += 1

            elif percentChangeRawA < -0.1 and percentChangeRawB > -0.1 and percentChangeRawB < 0.1:
                typeOfInteraction = 'Amensalism'
                countAmensalism += 1

            elif percentChangeRawA > -0.1 and percentChangeRawA < 0.1 and percentChangeRawB > 0.1:
                typeOfInteraction = 'Commensalism'
                countCommensalism += 1

            elif percentChangeRawA > -0.1 and percentChangeRawA < 0.1 and percentChangeRawB < -0.1:
                typeOfInteraction = 'Amensalism'
                countAmensalism += 1

            elif percentChangeRawA > -0.1 and percentChangeRawA < 0.1 and percentChangeRawB > -0.1 and percentChangeRawB < 0.1:
                typeOfInteraction = 'Neutralism'
                countNeutralism += 1

            else:
                typeOfInteraction = 'Empty'
                cherrypy.log('Attention! For model %s , an interaction was identified as Empty. Something is wrong!' %item[0])#todo print out to user

        except Exception as e:
            print e

        

        # Create the interactions table. See what the growth rates file looks like, and get the appropriate columns from there, and merge the information with the information in the file with the growth rates.

        print>>interactionsTableFile, item,'\t', percentChangeRawA,'\t', percentChangeRawB, '\t', typeOfInteraction


    # Report the counts for each interaction type.
    cherrypy.log("We finished creating the interactions table, and saved it to the file %s ." %interactionsTableFile)
    cherrypy.log("We counted %d interactions that were identified as Mutualism." %countMutualism)
    cherrypy.log("We counted %d interactions that were identified as Parasitism." %countParasitism)
    cherrypy.log("We counted %d interactions that were identified as Commensalism." %countCommensalism)
    cherrypy.log("We counted %d interactions that were identified as Competition." %countCompetition)
    cherrypy.log("We counted %d interactions that were identified as Amensalism." %countAmensalism)
    cherrypy.log("We counted %d interactions that were identified as Neutralism." %countNeutralism)

        
    interactionsTableFile.close()
