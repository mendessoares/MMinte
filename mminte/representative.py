from os.path import join, abspath, dirname
from Bio import SeqIO
from Bio.Blast.Applications import NcbiblastnCommandline
from mackinac import get_modelseed_model_stats, reconstruct_modelseed_model, gapfill_modelseed_model, \
    create_cobra_model_from_modelseed_model
from mackinac.SeedClient import ObjectNotFoundError
from cobra.io import save_json_model

mminte_folder = abspath(join(dirname(abspath(__file__)), '..'))
data_folder = join(mminte_folder, 'data')


def get_unique_otu_sequences(correlation_filename, sequence_filename, output_filename):
    """ Get the 16S rDNA sequences for the unique OTUs from a correlation file.

        The correlation file describes the relationship between all OTUs in the analysis
        and has three columns: (1) OTU identifier for first organism, (2) OTU identifier
        for second organism, (3) association between organisms (typically correlation or
        co-occurrence but can be any measure).

        The sequence file is a fasta file with the 16S rDNA sequences for all of the
        OTUs in the analysis.

    Parameters
    ----------
    correlation_filename : str
        Path to file with correlations for pairs of OTUs
    sequence_filename : str
        Path to file with 16S rDNA sequences for all OTUs
    output_filename: str
        Path to file with 16S rDNA sequences for unique OTUs

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

    # Find the 16S rDNA sequences for the unique OTUs.
    sequences = list()
    for record in SeqIO.parse(sequence_filename, 'fasta'):
        if record.id in unique_otu:
            sequences.append(record)

    # Store the unique sequences in the output file.
    SeqIO.write(sequences, output_filename, 'fasta')

    return len(sequences)


def search(sequence_filename, output_folder):
    """ Search for matches to known organisms from included 16S database.

    Parameters
    ----------
    sequence_filename : str
        Path to file with 16S rDNA sequences for unique OTUs
    output_folder: str
        Path to folder where blast output file is saved

    Returns
    -------
    list of str
        List of PATRIC genome IDs for known organisms

    Raises
    ------
    Bio.Application.ApplicationError
        When there is an error running the blast command
    """

    # @todo Need to figure out how to install blast during package install

    # Run blast to search for matches to known organisms.
    blast_cmd = join(mminte_folder, 'mminte/ncbi-blast-2.2.22+/bin/blastn')
    output_file = join(output_folder, 'blast.txt')
    cmdline = NcbiblastnCommandline(cmd=blast_cmd,
                                    query=sequence_filename,
                                    db=join(data_folder, 'db', '16Sdb'),
                                    out=output_file,
                                    outfmt=6,
                                    max_target_seqs=1,
                                    num_threads=4)
    cmdline()  # This can raise an ApplicationError

    # Parse the blast output file with the results. In output format 6, the second
    # field is the ID of match in target database. In our case that is the PATRIC
    # genome ID of the organism with the matching 16S sequence.
    genome_ids = set()
    query_ids = set()
    similarity = list()
    with open(output_file, 'r') as handle:
        for line in handle:
            fields = line.split()
            genome_ids.add(fields[1])
            if fields[0] not in query_ids:
                query_ids.add(fields[0])
                similarity.append((fields[0], fields[1], fields[2]))

    # Maybe build a pandas DataFrame which includes the target IDs in a column, extract them later.

    return list(genome_ids), similarity


def create_organism_models(genome_ids, output_folder):
    """ Create organism models from a list of PATRIC genome IDs.

    Parameters
    ----------
    genome_ids : list of str
        List of PATRIC genome IDs
    output_folder: str
        Path to folder where single organism models are stored

    Returns
    -------
    list of str
        List of paths to single organism model files
    """

    # @todo What if modelseed is weird, no model object error. Maybe it is just me
    models = list()
    for genome_id in genome_ids:
        try:
            stats = get_modelseed_model_stats(genome_id)
        except ObjectNotFoundError:
            stats = reconstruct_modelseed_model(genome_id)
            stats = gapfill_modelseed_model(stats['id'])

        model = create_cobra_model_from_modelseed_model(stats['id'])
        model_filename = join(output_folder, '{0}.json'.format(stats['id']))
        save_json_model(model, model_filename)
        models.append(model_filename)

    return models
