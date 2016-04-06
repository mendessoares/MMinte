import cherrypy
#cherrypy.config.update({"response.timeout":1000000,'log.access_file': '../supportFiles/logs/logAccess_file.txt','log.error_file': '../supportFiles/logs/logError_file.txt','log.screen': True})



def getUniqueOTU(corrs):
    '''

    In this function we use a file with three columns: columns 1 and 2 are lists of identifiers of OTUs from the microbiome study the user is interested in exploring. The third column has some value of associaltion between each pair of OTUs. The usual measure is correlation or co-occurrence, but it can be any measure of association really. This function goes through all the identifiers and creates a list of unique identifiers in the table, that is, all the different OTUs that are going to be part of the analsysi.

    :param corrs: file with the values of association between pairs of OTUs
    :returns uniqueOTUs: list with unique identifiers of OTUs
    '''

    cherrypy.log('We started the function to get the list of all unique OTUs from the file that lists how pairs of OTUs are correlated. The file we are using is %s .' %corrs)


    correlations = open(corrs,'r')
    correlations.readline()

    OTUs = []
    for line in correlations:
        line = line.rstrip().split()
        OTUs.append(line[0])
        OTUs.append(line[1])
    
    uniqueOTUs = list(set(OTUs))

    cherrypy.log('We created a list with %d unique OTUS.' %len(uniqueOTUs))


    return uniqueOTUs



    
def getSeqs(sequences):
  
    '''
    In this function, we "clean up" a FASTA file. The input is a FASTA file containing the 16S rDNA sequences of all the OTUs in the microbiome study the user is exploring. This function makes sure that each genomic sequence only spans one line in the file.

    :param sequences: FASTA file with 16S dRNA sequences spanning multiple lines in addition to the sequence identifier line.
    :returns seqs: list of 16s dRNA sequences in the FASTA format spanning only one line in addition to the sequence identifier line.
    '''
    

    cherrypy.log("We are now going to clean up the FASTA file given (%s) so that each DNA sequence does not span multiple lines."%sequences)

    userSeqs = open(sequences,'r')

    seq = ''

    for line in userSeqs:
        if line.startswith('>'):
            seq += '+++++\n'
            seq += line
        else:
            seq += line.rstrip()
        
    
    seqs = seq.split('+++++\n')

    userSeqs.close()


    cherrypy.log("Clean up is finished.  We are ready to fetch only the representative OTU sequences that we are interested in using in the rest of our analysis." )

    return seqs



def workingOTUs(uniqueOTUs,seqs, output):
    '''
    This function takes the outputs of the functions getUniqueOTU() and getSeqs(). It then creates a FASTA file that contains the 16S dRNA sequences for only the OTUs that are listed in the file with the association values between OTUs. This reduces the size of the files to ge used in further analysis in MMinte.


    :param uniqueOTUs: list of OTUs present in the dataset with association information, output of getUniqueOTU()
    :param seqs: set of sequences in a FASTA file where the sequences themselves only take one line and do not span multiple lines
    :param output: FASTA file with only the sequences that are needed for running Widget 2
    :returns output: FASTA file with only the sequences that are needed for running Widget 2

    '''

    cherrypy.log('Finally, we are going to create a FASTA file with only the representative OTUs that we will use in our analysis.')
    cherrypy.log('The full path to the FASTA file created is %s .' %output)

    reprOtusForAnalysis = open(output,'w')
    counter = 0
    for line in seqs:
        for item in uniqueOTUs:
            new_item = '>'+item+' '
            if line.startswith(new_item):
                counter += 1
                print>>reprOtusForAnalysis, line
        
    reprOtusForAnalysis.close() 


    cherrypy.log("There are a total of %d sequences to BLAST against the local database. The path to this file is %s"%(counter,output))
