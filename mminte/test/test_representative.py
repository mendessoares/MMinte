import pytest
from os import unlink
from os.path import join
from Bio.Application import ApplicationError

import mminte


class TestRepresentative:

    def test_representative(self, data_folder, test_folder):
        correlations = mminte.read_correlation_file(join(data_folder, 'correlation.txt'))
        sequence_filename = join(data_folder, 'all_otus.fasta')
        unique_filename = join(test_folder, 'unique_otus.fasta')
        num_sequences = mminte.get_unique_otu_sequences(correlations, sequence_filename, unique_filename)
        assert num_sequences == 18

        blast_filename = join(test_folder, 'blast.txt')
        genome_ids, similarity = mminte.search(unique_filename, blast_filename)
        assert len(genome_ids) == 18
        assert len(similarity) == 18
        assert '484018.6' in genome_ids

        unlink(unique_filename)
        unlink(blast_filename)

    def test_missing_otu(self, data_folder, test_folder):
        correlations = mminte.read_correlation_file(join(data_folder, 'correlation.txt'))
        sequence_filename = join(data_folder, 'missing.fasta')
        unique_filename = join(test_folder, 'unique_otus.fasta')
        with pytest.raises(ValueError):
            mminte.get_unique_otu_sequences(correlations, sequence_filename, unique_filename)

    def test_bad_all_sequence_file(self, data_folder, test_folder):
        correlations = mminte.read_correlation_file(join(data_folder, 'correlation.txt'))
        sequence_filename = join(data_folder, 'BAD.fasta')
        unique_filename = join(test_folder, 'unique_otus.fasta')
        with pytest.raises(IOError):
            mminte.get_unique_otu_sequences(correlations, sequence_filename, unique_filename)

    def test_bad_unique_sequence_file(self, data_folder, test_folder):
        unique_filename = join(data_folder, 'BAD.fasta')
        blast_filename = join(test_folder, 'blast.txt')
        with pytest.raises(ApplicationError):
            mminte.search(unique_filename, blast_filename)

    def test_bad_correlation_file(self, data_folder):
        with pytest.raises(IOError):
            mminte.read_correlation_file(join(data_folder, 'BAD.txt'))

    def test_invalid_correlation_fields(self, data_folder):
        with pytest.raises(ValueError):
            mminte.read_correlation_file(join(data_folder, 'correlation_fields.txt'))

    def test_invalid_correlation_value(self, data_folder):
        with pytest.raises(ValueError):
            mminte.read_correlation_file(join(data_folder, 'correlation_value.txt'))

    def test_bad_similarity_file(self, data_folder):
        with pytest.raises(IOError):
            mminte.read_similarity_file(join(data_folder, 'BAD.csv'))
