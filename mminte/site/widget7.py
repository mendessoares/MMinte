import cherrypy
#cherrypy.config.update({"response.timeout":1000000,'log.access_file': '../supportFiles/logs/logAccess_file.txt','log.error_file': '../supportFiles/logs/logError_file.txt','log.screen':True})

'''
    The goal of the functions in this file is to gather information from several sources (table) to create a json file that will be  used for plotting the network using D3.js
'''

def nodes(inNodes):
    '''
    This function takes the information present in the file listing the percent similarity between the 16S dRNA sequence of the OTUs used in the analysis and the 16S dRNA sequence from the local database (output of Widget 2), assings a score reflecting the percent similarity value, and creates a list of dictionaries where the keys match the keys identified by the plotting script to create the NODES of the network.

    :param inNodes: file with the information about the percent similarity between the 16S sequence of the OTUs of interest and the 16S sequences present in the local database.
    :return nodes_value: list of dictionaries with the information for each node in the network.
    '''

    nodesFile = open(inNodes,'r')
    nodesFile.readline()

    cherrypy.log("We opened the function nodes. This will create a dictionary with the information that needs to go into the json file to be fed to the D3 plotting. The file that provides the node information is %s" %inNodes)

    nodesTable = []
    counter = 0
    for i in nodesFile:
        i = i.rstrip()
        i = i.split()

        # Assign a similarity score to the percent similarity
        if float(i[3]) >= 99.00:
            similScore = 1
        elif float(i[3]) >= 95.00:
            similScore = 2
        elif float(i[3]) >= 90.00:
            similScore = 3
        elif float(i[3]) >= 70.00:
            similScore = 4
        elif float(i[3]) >= 50.00:
            similScore = 5
        else:
            similScore = 6

        new_line = i[0],i[1],i[2],i[3],similScore,'...'.join(i[1:3])

        # Create a new table that includes the information that was previously in the table PLUS the similarity score PLUS an extra column containing the info about the OTU id and the genomeID.

        nodesTable.append(new_line)

    cherrypy.log('The table with the initial infomation about all the nodes has %d entries. All this information will now be transferred to a list of dictionaries. Each dictionary will have 2 entries; one for the name which is the otu identifier connected to the genomeID it was mathed with, and the other from a key called group with the value matching a similarity score.' %counter)

    node_value = []
        
    for i in nodesTable:
        new_node = {'name':i[5],'group':int(i[4])}
        node_value.append(new_node)

    return node_value





def links(inNodes,inLinks, inInter):
    '''
    This function organizes the information that is present in three different files and creates a list of dictionaries where the keys match the keys identified by the plotting script to create the LINKS of the network. The first file lists the percent similarity between the 16S dRNA sequence of the OTUs used in the analysis and the 16S dRNA sequence from the local database (output of Widget 2). This file is used to match the ids of the OTUs to the correspondng genome ID. The second file contains the association values between pairs of OTUs (same file used in Widget 1). This file is used to create the information abou the links between OTUs that will be the base for the network plotting. The correlation values are transformed to a discrete score. Finally, the third file contains the information contained in the file with growth rates, plus information regarding the the types of interactions predicted to be occurring in the community. This file is used to assigne a color to the links between OTUs. Positive interactions (mutualism, commensalism) are colored green, negative interactions (competition, parasitism and amensalism) are colored red, and no significant interaction between the species (neutralism) is depicted with grey.


    :param inNodes: ile with the information about the percent similarity between the 16S sequence of the OTUs of interest and the 16S sequences present in the local database.
    :param inLinks: file with the values of association between pairs of OTUs
    :param inInter: file with the interactions that are predicted to be occurring between species in a two-species community
    :return link_value: list of dictionaries with the information needed to plot the links in the interaction network plot
    '''




    inNodesFile = inNodes
    inLinksFile = inLinks
    inInterFile = inInter

    cherrypy.log('We are now going to create a dictionary that has the information for the links in our network. For this we use 3 files: %s, %s and %s'%(inNodesFile,inLinksFile,inInterFile))

    similFile = open(inNodesFile,'r')
    similTable = []
    for i in similFile:
        i = i.rstrip()
        i = i.split()
        similTable.append(i)


    corrsFile = open(inLinksFile, 'r')
    corrsTable = []
    for i in corrsFile:
        i = i.rstrip()
        i = i.split()
        corrsTable.append(i)




    ############

    # Create temporary table that will list ID of the species that matches the ID of the OTU listed in the otuA column. Also, create a extra column with the correlation score defined by the value of the correlation between the OTUs.
    tempTableA = []
    first_line = 'otuA','otuB','correlation','correlationScore','speciesA','rowNumA'
    tempTableA.append(list(first_line))

    for i in corrsTable:
        for j in similTable:
            if i[0] == j[1]:
                if float(i[2]) >= 0.99:
                    corrScore = 1
                elif float(i[2]) >= 0.90:
                    corrScore = 2
                elif float(i[2]) >= 0.70:
                    corrScore = 3
                elif float(i[2]) >= 0.50:
                    corrScore = 4
                elif float(i[2]) >= 0.00:
                    corrScore = 5
                elif float(i[2]) >= -0.10:
                    corrScore = 6
                elif float(i[2]) >= -0.50:
                    corrScore = 7
                elif float(i[2]) >= -0.70:
                    corrScore = 8
                else:
                    corrScore = 9

                new_line = i[0],i[1],i[2],corrScore,j[2],j[0]
                tempTableA.append(list(new_line))
            else:
                continue

    cherrypy.log('We started by creating a temporary table that has the information with the id of otuA and its matching speciesID. We called this table tempTableA and it is finished.')

    # Create temporary table that will list ID of the species that matches the ID of the OTU listed in the otuB column.
    tempTableB = []
    first_line = 'otuA','otuB','correlation','correlationScore','speciesA','speciesB','rowNumA','rowNumB'
    tempTableB.append(list(first_line))

    for i in tempTableA:
        for j in similTable:
            if i[1] == j[1]:
                new_line = i[0],i[1],float(i[2]),i[3],i[4],j[2],int(i[5]),int(j[0])
                tempTableB.append(list(new_line))
            else:
                continue


    ############################
    cherrypy.log('We then created another temporary table, tempTableB, that includes the information about the speciesID that matches otuB. It is now finished.')

    # Create temporary table that will contain all the information that is needed to create the list of dictionaries with the information for drawing the LINKS of the network.
    tempTableC = []
    first_line = 'otuA','otuB','speciesA','speciesB','rowNumA','rowNumB','correlation','correlationScore','interactionType','interactionScore'
    tempTableC.append(list(first_line))

    interactionsFile = open(inInterFile, 'r')
    interactionsTable = []
    for i in interactionsFile:
        i = i.rstrip()
        i = i.split()
        interactionsTable.append(i)


    cherrypy.log('We are now going to create a table with the previous information and translate the interactions previously defined into positive, negative or no interactions.')

    countPositive = 0
    countNegative = 0
    countNoInteraction = 0
    countSomethingsWrong = 0


    for i in interactionsTable:
        for j in tempTableB:
            if i[1] == j[4] and i[2] == j[5]:
                if i[9] == 'Mutualism':
                    interactionsScore = 2
                    countPositive += 1
                    print i[1],j[4],i[2],j[5],i[9],interactionsScore

                elif i[9] == 'Parasitism':
                    interactionsScore = 1
                    countNegative += 1
                    print i[1],j[4],i[2],j[5],i[9],interactionsScore

                elif i[9] == 'Commensalism':
                    interactionsScore = 2
                    countPositive += 1
                    print i[1],j[4],i[2],j[5],i[9],interactionsScore

                elif i[9] == 'Competition':
                    interactionsScore = 1
                    countNegative += 1
                    print i[1],j[4],i[2],j[5],i[9],interactionsScore

                elif i[9] == 'Neutralism':
                    interactionsScore = 0
                    countNoInteraction += 1
                    print i[1],j[4],i[2],j[5],i[9],interactionsScore

                elif i[9] == 'Amensalism':
                    interactionsScore = 1
                    countNegative += 1
                    print i[1],j[4],i[2],j[5],i[9],interactionsScore

                else:
                    print i[9]
                    interactionsScore = 10
                    countSomethingsWrong += 1
                    print i[1],j[4],i[2],j[5],i[9],interactionsScore

                new_line = j[0],j[1],j[4],j[5],j[6],j[7],j[2],j[3],i[9],interactionsScore
                tempTableC.append(list(new_line))

            elif i[1] == j[5] and i[2] == j[4]:
                if i[9] == 'Mutualism':
                    interactionsScore = 2
                    countPositive += 1
                    print i[1],j[5],i[2],j[4],i[9],interactionsScore

                elif i[9] == 'Parasitism':
                    interactionsScore = 1
                    countNegative += 1
                    print i[1],j[5],i[2],j[4],i[9],interactionsScore

                elif i[9] == 'Commensalism':
                    interactionsScore = 2
                    countPositive += 1
                    print i[1],j[5],i[2],j[4],i[9],interactionsScore

                elif i[9] == 'Competition':
                    interactionsScore = 1
                    countNegative += 1
                    print i[1],j[5],i[2],j[4],i[9],interactionsScore

                elif i[9] == 'Neutralism':
                    interactionsScore = 0
                    countNoInteraction += 1
                    print i[1],j[5],i[2],j[4],i[9],interactionsScore

                elif i[9] == 'Amensalism':
                    interactionsScore = 1
                    countNegative += 1
                    print i[1],j[5],i[2],j[4],i[9],interactionsScore

                else:
                    print i[9]
                    interactionsScore = 10
                    countSomethingsWrong +=1

                new_line = j[0],j[1],j[4],j[5],j[6],j[7],j[2],j[3],i[9],interactionsScore
                tempTableC.append(list(new_line))

            else:
                continue

    cherrypy.log('We finished creating a last table with the matches between otus and their speciesID, and the interactions occurring between them, and whether these are positive, negative, no interactions, or if there was something wrong.')
    cherrypy.log('We found %d Positive interactions' %countPositive)
    cherrypy.log('We found %d Negative interactions' %countNegative)
    cherrypy.log('We found %d No interactions' %countNoInteraction)
    cherrypy.log('There was something wrong with the interaction assignments %d times' %countSomethingsWrong)

    print countPositive
    print countNegative
    print countNoInteraction
    print countSomethingsWrong


    link_value = []

    for i in tempTableC:
        try:
            new_link = {"source":int(i[4]),"target":int(i[5]),"value":int(i[7]),"interaction":int(i[9])}
            link_value.append(new_link)
        except:
            continue

    cherrypy.log('We finished creating a list of dictionaries with the information about the links in our network')
    return link_value

def createJSONforD3(node_value,link_value):
    '''
    This function takes the variables created in the functions nodes() and links() and creates a json file that contains all the necessary information for plotting the netwrok of associations between the different OTUs with the color of the links reflecting the prediction of the types of interactions occurring between pairs of OTUs.

    :param node_value: list of dictionaries returned from function nodes
    :param link_value: list of dictionaries returned from function links
    :return data4plot_json: file in json format in site folder that contains the information required for plotting network of associations between OTUs and the predicted interactions occurring between pairs of species.
    '''

    import json
    cherrypy.log('Finally, we will dump the information about the nodes and links of our network to a json file.')

    '''
    @summary: put the nodes values and the links values into the final dataset that is in the dictionary format
    ''' 
    dataDict = {'nodes': node_value, 'links': link_value}


    '''
    @summary: dump the new data into a json file
    '''
    
    with open('data4plot_json','w') as outfile:
        cherrypy.log('The information will be dumped into the file %s' %outfile)
        json.dump(dataDict, outfile)
        
    cherrypy.log('We finished creating the json file.')