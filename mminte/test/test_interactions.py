import pytest
import json
from os import unlink
from os.path import join

import mminte


class TestInteractions:

    def test_growth_rates(self, data_folder, test_folder):
        model_files = ['BT.sbml', 'FP.sbml']
        source_models = mminte.get_all_pairs([join(data_folder, x) for x in model_files])
        pair_models = mminte.create_interaction_models(source_models, test_folder)
        assert len(pair_models) == 1
        assert pair_models[0] == '{0}/BTxFP.json'.format(test_folder) or \
               pair_models[0] == '{0}/FPxBT.json'.format(test_folder)

        western = json.load(open(join(data_folder, 'western.json')))
        growth_rates = mminte.calculate_growth_rates(pair_models, western)
        assert growth_rates.at[0, 'A_ID'] == 'BT'
        assert growth_rates.at[0, 'B_ID'] == 'FP'
        assert growth_rates.at[0, 'TYPE'] == 'Parasitism'
        assert growth_rates.at[0, 'TOGETHER'] == pytest.approx(0.49507501)
        assert growth_rates.at[0, 'A_TOGETHER'] == pytest.approx(0.27746256)
        assert growth_rates.at[0, 'B_TOGETHER'] == pytest.approx(0.21761245)
        assert growth_rates.at[0, 'A_ALONE'] == pytest.approx(0.44073842)
        assert growth_rates.at[0, 'B_ALONE'] == pytest.approx(0.16933796)
        assert growth_rates.at[0, 'A_CHANGE'] == pytest.approx(-0.37045977)
        assert growth_rates.at[0, 'B_CHANGE'] == pytest.approx(0.28507777)

        for model in pair_models:
            unlink(model)

    def test_not_enough_source(self, data_folder, test_folder):
        with pytest.raises(ValueError):
            mminte.create_interaction_models([(join(data_folder, 'BT.sbml'))], test_folder)

    def test_bad_source_file(self, data_folder, test_folder):
        model_files = ['BT.sbml', 'BAD.sbml']
        source_models = mminte.get_all_pairs([join(data_folder, x) for x in model_files])
        with pytest.raises(IOError):
            mminte.create_interaction_models(source_models, test_folder)

    def test_bad_extension(self, data_folder, test_folder):
        model_files = ['BT.sbml', 'FP.bad']
        source_models = mminte.get_all_pairs([join(data_folder, x) for x in model_files])
        with pytest.raises(IOError):
            mminte.create_interaction_models(source_models, test_folder)

    def test_bad_growth_rates_file(self, data_folder):
        with pytest.raises(IOError):
            mminte.read_growth_rates_file(join(data_folder, 'BAD.csv'))

    def test_bad_diet_file(self, data_folder):
        with pytest.raises(IOError):
            mminte.read_diet_file(join(data_folder, 'BAD.txt'))

    def test_invalid_diet_fields(self, data_folder):
        with pytest.raises(ValueError):
            mminte.read_correlation_file(join(data_folder, 'diet_fields.txt'))

    def test_invalid_diet_value(self, data_folder):
        with pytest.raises(ValueError):
            mminte.read_correlation_file(join(data_folder, 'diet_value.txt'))

    def test_create_species_model(self, test_folder):
        single_models = mminte.create_species_models(['226186.12'], test_folder)
        assert len(single_models) == 1
        assert single_models[0] == test_folder + '/226186.12.json'
        unlink(single_models[0])
