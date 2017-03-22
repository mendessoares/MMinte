from os import unlink
from os.path import join
from tempfile import gettempdir

import mminte


class TestRepresentative:

    def test_representative(self, data_folder):
        correlation_filename = join(data_folder, 'correlation.txt')
        sequence_filename = join(data_folder, 'all_otus.fasta')
        unique_filename = join(gettempdir(), 'unique_otus.fasta')
        num_sequences = mminte.get_unique_otu_sequences(correlation_filename, sequence_filename, unique_filename)
        assert num_sequences == 18

        blast_filename = join(gettempdir(), 'blast.txt')
        genome_ids, similarity = mminte.search(unique_filename, blast_filename)
        assert len(genome_ids) == 18
        assert len(similarity) == 18
        assert '484018.6' in genome_ids

        unlink(unique_filename)
        unlink(blast_filename)
