import cherrypy
#cherrypy.config.update({"response.timeout":1000000,'log.access_file': '../supportFiles/logs/logAccess_file.txt','log.error_file': '../supportFiles/logs/logError_file.txt','log.screen':True})


tempOutputFile = '../tempFiles/blastOutput.txt'

def blastSeqs(seqsToBlast):
    '''
    This function uses an input FASTA file with genomic sequences of 16S dRNA and BLASTs each sequence against a local database (found in supportFiles/db/) that contains the 16S dRNA sequences of all the bacterial species in the PATRIC database that have a whole genome sequence available. It output only the top hit to a tab-delimeted text file. The 16S sequences present in the database were provided by Maulik Shukla on the 3rd of November of 2015.

    :param seqsToBlast: FASTA file containing the sequences that will be matched to the sequences in the local database. Called in blastn from parameter query.
    :param dbase: local database on ../supportFiles/db/16Sdb. Called in blastn from parameter db.
    :param tempOutputFile:  global variable defined by file on '../tempFiles/blastOutput.txt'. Raw BLAST results are temporarily stored in this file and will be processed in function listTaxId4ModelSEED(). Called in blastn from parameter out.
    :returns tempOutputFile


    '''



    from Bio.Blast.Applications import NcbiblastnCommandline
    import os

    cherrypy.log('We will blast the sequences in the FASTA file provided, %s, against a local custom database that contains the 16S sequences of the species in the NCBI that have whole genome sequences.' %(seqsToBlast))

    dbase = '../supportFiles/db/16Sdb'

    
    '''
    @summary: run a local blast of the user's representative OTUs, the output format is tabular, only one match is shown
    '''

    blastn_cline = NcbiblastnCommandline(cmd='../ncbi-blast-2.2.22+/bin/blastn', query= seqsToBlast, db= dbase, outfmt= 6, out= tempOutputFile, max_target_seqs = 1, num_threads = 5)

    cherrypy.log('The BLAST command that will be run is: %s' %blastn_cline)

    os.system(str(blastn_cline))


    #check if the tempOutputFile file was created. if not, shout out an error.

    if os.stat(tempOutputFile).st_size != 0:
        cherrypy.log('The %s was created and it is not empty' %tempOutputFile)
    else:
        cherrypy.log('Something is wrong because the %s appears to be empty' %tempOutputFile)
        exit()

    

    
def listTaxId4ModelSEED(outputSimil,outputIDs):
    '''
    Once the blast run is done, listTaxId4ModelSEED processes the output (in tempOutputFile) so that it creates two files. One contains the list of models that will be created using ModelSeed. The other is a file with information about the percent similarity between the sequences of the queried OTUs and the matching sequences from the local database. It contains four columns. The first column is the row number this will be used in the plotting of the interaction network in Widget 7. The second row lists the identifiers of the OTUs whose 16S seqeunces were blasted against the local 16S database. The third column lists the ID of he genome whose species the sequence of the query OTU matched. The fourth column lists the percent similarity values bwteen the queried sequence and the match in the database.

    :param outputSimil: file that will contain the information about the percent similarity between queried OTUs and matching database sequences.
    :param outputIDs: file that will contain the list of genome IDs for the models that will be reconstructed using the ModelSEED platform.
    :returns outputSimil
    :returns outputIDs
    '''

    cherrypy.log('We will now create 2 files %s and %s. The first one as a table with the results from BLAST, with the information about the percent similarity between the OTU queried and the sequence it was matched to. The second one has a list of the genomeIDs for the bacteria that we will reconstruct and get metabolic models for.' %(outputSimil,outputIDs))

    blastResultsFile = open(tempOutputFile, 'r')
    cleanBlastResultsFile = open(outputSimil,'w')
    ids4MSFile = open(outputIDs,'w')

    print>>cleanBlastResultsFile, 'Row number', '\t', 'Query_Otu_ID','\t','Species_ID','\t' ,'Percent_ID'
    
    ids4MS = []
    blastTable = []

    
    for i in blastResultsFile:
        item = i.split()
        ids4MS.append(item[1])
        blastTable.append(item)
        

    cleanBlastResultsTable = []    
    uniqueRows = []    
    
    for x in blastTable:
        if x[0] not in uniqueRows:
            cleanBlastResultsTable.append(x)
            uniqueRows.append(x[0])

    
    counter = 0 
    
    for i in cleanBlastResultsTable:
        print>>cleanBlastResultsFile, counter, '\t',i[0],'\t',i[1],'\t',i[2]
        counter += 1

    cleanBlastResultsFile.close()
    cherrypy.log('The %s was created and it has %d rows'%(outputSimil,counter))

    cleanIds4MS=list(set(ids4MS))
    
    blastResultsFile.close()
    
    for i in cleanIds4MS:
        print>>ids4MSFile, i

    cherrypy.log('The %s file was created. In total, we will reconstruct %d models in widget 3.' %(outputIDs,len(cleanIds4MS)))
    
    ids4MSFile.close()


    print "Done."
