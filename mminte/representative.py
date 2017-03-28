import pkg_resources
from os.path import join
from Bio import SeqIO
from Bio.Blast.Applications import NcbiblastnCommandline
import pandas as pd


# Column names for similarity information data frame.
similarity_columns = ['OTU_ID', 'GENOME_ID', 'SIMILARITY']


def get_unique_otu_sequences(correlation_filename, sequence_filename, output_filename):
    """ Get the 16S rDNA sequences for the unique OTUs from a correlation file.

    The correlation file describes the relationship between OTUs in the analysis
    and has three columns: (1) OTU identifier for first organism, (2) OTU identifier
    for second organism, (3) association between organisms (typically correlation or
    co-occurrence but can be any measure).

    The sequence file is a fasta file with the 16S rDNA sequences of the OTUs in the
    analysis. The record ID in each fasta record must be an OTU number.  All of the
    OTUs in the correlation file must have a record in the fasta file.

    Parameters
    ----------
    correlation_filename : str
        Path to file with correlations for pairs of OTUs
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
    with open(correlation_filename, 'r') as handle:
        handle.readline()  # Skip header line
        for line in handle:
            line = line.rstrip().split()
            unique_otu.add(line[0])
            unique_otu.add(line[1])

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

    # @todo Need to understand why there is entry with 0% similarity.

    # Parse the blast output file with the results. In output format 6, the second
    # field is the ID of match in target database. In our case that is the PATRIC
    # genome ID of the organism with the matching 16S sequence.
    genome_ids = set()
    query_ids = set()
    similarity = pd.DataFrame(columns=similarity_columns)
    with open(output_filename, 'r') as handle:
        for line in handle:
            fields = line.split()
            genome_ids.add(fields[1])
            if fields[0] not in query_ids:
                query_ids.add(fields[0])
                similarity = similarity.append(pd.Series([fields[0], fields[1], fields[2]],
                                                         index=similarity_columns),
                                               ignore_index=True)

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
