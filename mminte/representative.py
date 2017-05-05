import pkg_resources
from os.path import join
from Bio import SeqIO
from Bio.Blast.Applications import NcbiblastnCommandline
import pandas as pd
from warnings import warn


# Column names for similarity information data frame.
similarity_columns = ['OTU_ID', 'GENOME_ID', 'SIMILARITY']


def get_unique_otu_sequences(correlations, sequence_filename, output_filename):
    """ Get the 16S rDNA sequences for the unique OTUs from a correlation file.

    The list of correlations describes the relationship between OTUs in the analysis.
    Each entry in the list is a tuple with three elements: (1) OTU identifier for 
    first organism, (2) OTU identifier for second organism, (3) association between 
    organisms (typically correlation or co-occurrence but can be any measure).

    The sequence file is a fasta file with the 16S rDNA sequences of the OTUs in the
    analysis. The record ID in each fasta record must be an OTU number.  All of the
    OTUs in the correlation file must have a record in the fasta file.

    Parameters
    ----------
    correlations : list of tuple
        Each tuple has first OTU ID (str), second OTU ID (str), and correlation value (float)
    sequence_filename : str
        Path to fasta file with 16S rDNA sequences for all OTUs
    output_filename: str
        Path to fasta file with 16S rDNA sequences for unique OTUs

    Returns
    -------
    int
        Number of sequences in output file
    """

    # Find all of the unique OTUs in the correlation file.
    unique_otu = set()
    for corr in correlations:
        unique_otu.add(corr[0])
        unique_otu.add(corr[1])

    # Find the 16S rDNA sequences for the unique OTUs in the fasta file.
    sequences = list()
    found_otu = set()
    for record in SeqIO.parse(sequence_filename, 'fasta'):
        if record.id in unique_otu:
            sequences.append(record)
            found_otu.add(record.id)

    # Make sure all of the OTUs from the correlation file have a 16S rDNA
    # sequence in the fasta file.
    missing_otu = unique_otu - found_otu
    if len(missing_otu) > 0:
        raise ValueError('Sequence fasta file "{0}" does not contain records for OTUs: {1}'
                         .format(sequence_filename, missing_otu))

    # Store the unique sequences in the output file.
    SeqIO.write(sequences, output_filename, 'fasta')

    return len(sequences)


def search(sequence_filename, output_filename):
    """ Search for matches to known organisms from included 16S database.

    Parameters
    ----------
    sequence_filename : str
        Path to file with 16S rDNA sequences for unique OTUs
    output_filename: str
        Path to file where blast output file is saved

    Returns
    -------
    list of str
        List of PATRIC genome IDs for known organisms
    pandas.DataFrame
        Similarity information with OTU ID, genome ID, and percent similarity of match

    Raises
    ------
    Bio.Application.ApplicationError
        When there is an error running the blast command
    """

    # Run blast to search for matches to known organisms.
    # @todo Should it make me nervous to not use a fully-qualified path here?
    cmdline = NcbiblastnCommandline(cmd='blastn',
                                    query=sequence_filename,
                                    db=join(pkg_resources.resource_filename(__name__, 'data/db'), '16Sdb'),
                                    out=output_filename,
                                    outfmt=6,
                                    max_target_seqs=1,
                                    num_threads=4)
    cmdline()  # Raises ApplicationError when there is a problem

    # Parse the blast output file with the results. In output format 6, the first
    # field is the OTU ID from the query. The second field is the ID of match in
    # target database. In our case that is the PATRIC genome ID of the organism
    # with the matching 16S sequence. The third field is the percent similarity.
    genome_ids = set()
    query_ids = set()
    similarity = pd.DataFrame(columns=similarity_columns)
    with open(output_filename, 'r') as handle:
        for line in handle:
            fields = line.split()
            genome_ids.add(fields[1])
            if fields[0] not in query_ids:
                query_ids.add(fields[0])
                similarity = similarity.append(pd.Series([fields[0], fields[1], float(fields[2])],
                                                         index=similarity_columns),
                                               ignore_index=True)
            else:
                current = similarity.loc[similarity['OTU_ID'] == fields[0]]
                if current.iloc[0]['GENOME_ID'] != fields[1]:
                    warn('OTU {0} matches already matched genome {1} and also matches genome {2}'
                         .format(fields[0], current.iloc[0]['GENOME_ID'], fields[1]))

    return list(genome_ids), similarity


def read_similarity_file(similarity_filename):
    """ Read a file with the saved similarity data frame.

    Parameters
    ----------
    similarity_filename : str
        Path to file with similarity data frame in CSV format

    Returns
    -------
    pandas.DataFrame
        Similarity information with OTU ID, genome ID, and percent similarity of match
    """

    return pd.read_csv(similarity_filename, dtype={'OTU_ID': str, 'GENOME_ID': str})


def write_similarity_file(similarity, similarity_filename):
    """ Write a similarity data frame to a file.

    Parameters
    ----------
    similarity : pandas.DataFrame
        Similarity information with OTU ID, genome ID, and percent similarity of match
    similarity_filename : str
        Path to file for storing similarity data frame in CSV format
    """

    similarity.to_csv(similarity_filename, index=False)
    return


def read_correlation_file(correlation_filename):
    """ Read a file with the correlation between pairs of OTUs.

    The correlation file describes the relationship between OTUs in the analysis. Each
    line must have three fields and the first line of the file is a header line that
    is ignored. The first two fields are OTU IDs and the third field is a correlation
    value that must be in the range -1.0 to 1.0.

    Parameters
    ----------
    correlation_filename : str
        Path to file with correlations for pairs of OTUs

    Returns
    -------
    list of tuple
        Each tuple has first OTU ID (str), second OTU ID (str), and correlation value (float)
    """

    correlations = list()
    with open(correlation_filename, 'rU') as handle:
        handle.readline()  # Skip header line
        line_num = 1
        for line in handle:
            line_num += 1
            fields = line.strip().split()
            if len(fields) != 3:
                raise ValueError('Line {0} in file "{1}" must have three fields'
                                 .format(line_num, correlation_filename))
            value = float(fields[2])
            if value < -1.0 or value > 1.0:
                raise ValueError('Correlation value {0} on line {1} in file "{2}" is out of range'
                                 .format(value, line_num, correlation_filename))
            correlations.append((fields[0], fields[1], value))
    return correlations
