import logging
import os
import pathlib

import cudf

logger = logging.getLogger(__name__)

__all__ = ['ChEMBLApprovedDrugsPhyschem', 'MoleculeNetLipophilicityPhyschem', 'MoleculeNetESOLPhyschem', 'MoleculeNetFreeSolvPhyschem', 'ZINC15TestSplit', 'TABLE_LIST']
TABLE_LIST = ['chembl', 'lipophilicity', 'esol', 'freesolv', 'zinc15_test'] # must match datasets table_names

class GenericCSVDataset():
    def __init__(self, name=None, properties_cols=None, index_col=None, index_selection=None, data_path=None):
        self.name = name
        self.data_path = data_path
        self.data = None
        self.max_len = None
        self.properties = None

        self.properties_cols = properties_cols # TODO most of these should be passed during load
        self.index_col = index_col
        self.index_selection = index_selection

    def _load_csv(self, columns, length_column=None, return_remaining=True):
        columns = [columns] if not isinstance(columns, list) else columns
        data = cudf.read_csv(self.data_path)

        if self.index_col:
            data = data.set_index(self.index_col).sort_index()
        else:
            data.index.name = 'index'

        if self.index_selection:
            data = data.loc[self.index_selection]
            
        if length_column:
            self.max_len = data[length_column].max()
        elif len(columns) == 1:
            self.max_len = data[columns[0]].to_pandas().map(len).max()

        cleaned_data = data[columns]

        if return_remaining:
            if length_column:
                remain_columns = [x for x in data.columns if (x not in columns) & (x not in [length_column])]
            else:
                remain_columns = [x for x in data.columns if (x not in columns)]
            other_data = data[remain_columns]
        else:
            other_data = None
        return cleaned_data, other_data

    def load(self, columns=['canonical_smiles'], length_column='length'):
        self.data, _ = self._load_csv(columns, length_column)


class ChEMBLApprovedDrugsPhyschem(GenericCSVDataset):
    def __init__(self, **kwargs):
        super().__init__(kwargs)
        self.name = 'ChEMBL Approved Drugs (Phase III/IV)'
        self.table_name = 'chembl'
        self.properties_cols = ['max_phase_for_ind', 'mw_freebase', \
                           'alogp', 'hba', 'hbd', 'psa', 'rtb', 'ro3_pass', 'num_ro5_violations', \
                           'cx_logp', 'cx_logd', 'full_mwt', 'aromatic_rings', 'heavy_atoms', \
                           'qed_weighted', 'mw_monoisotopic', 'hba_lipinski', 'hbd_lipinski', \
                           'num_lipinski_ro5_violations']
        self.data_path = os.path.join(pathlib.Path(__file__).parent.parent.absolute(),
                                      'data',
                                      'benchmark_ChEMBL_approved_drugs_physchem.csv')
        assert os.path.exists(self.data_path)

    def load(self, columns=['canonical_smiles']):
        data, properties = self._load_csv(columns)
        properties = properties[self.properties_cols]
        self.data, self.properties = data, properties


class MoleculeNetLipophilicityPhyschem(GenericCSVDataset):
    def __init__(self, **kwargs):
        super().__init__(kwargs)
        self.name = 'MoleculeNet Lipophilicity'
        self.table_name = 'lipophilicity'
        self.properties_cols = ['logD']
        self.data_path = os.path.join(pathlib.Path(__file__).parent.parent.absolute(),
                                      'data',
                                      'benchmark_MoleculeNet_Lipophilicity.csv')
        assert os.path.exists(self.data_path)

    def load(self, columns=['smiles']):
        orig_property_name = ['exp']
        data, properties = self._load_csv(columns)
        data = data.rename(columns={columns[0]: 'canonical_smiles'})
        properties = properties.rename(columns=dict(zip(orig_property_name, self.properties_cols)))
        properties = properties[self.properties_cols]
        self.data, self.properties = data, properties


class MoleculeNetESOLPhyschem(GenericCSVDataset):
    def __init__(self, **kwargs):
        super().__init__(kwargs)
        self.name = 'MoleculeNet ESOL'
        self.table_name = 'esol'
        self.properties_cols = ['log_solubility_(mol_per_L)']
        self.data_path = os.path.join(pathlib.Path(__file__).parent.parent.absolute(),
                                      'data',
                                      'benchmark_MoleculeNet_ESOL.csv')
        assert os.path.exists(self.data_path)

    def load(self, columns=['smiles']):
        orig_property_name = ['measured log solubility in mols per litre']
        data, properties = self._load_csv(columns)
        data = data.rename(columns={columns[0]: 'canonical_smiles'})
        properties = properties.rename(columns=dict(zip(orig_property_name, self.properties_cols)))
        properties = properties[self.properties_cols]
        self.data, self.properties = data, properties


class MoleculeNetFreeSolvPhyschem(GenericCSVDataset):
    def __init__(self, **kwargs):
        super().__init__(kwargs)
        self.name = 'MoleculeNet FreeSolv'
        self.table_name = 'freesolv'
        self.properties_cols = ['hydration_free_energy']
        self.data_path = os.path.join(pathlib.Path(__file__).parent.parent.absolute(),
                                      'data',
                                      'benchmark_MoleculeNet_FreeSolv.csv')
        assert os.path.exists(self.data_path)

    def load(self, columns=['smiles']):
        orig_property_name = ['y']
        data, properties = self._load_csv(columns)
        data = data.rename(columns={columns[0]: 'canonical_smiles'})
        properties = properties.rename(columns=dict(zip(orig_property_name, self.properties_cols)))
        properties = properties[self.properties_cols]
        self.data, self.properties = data, properties


class ZINC15TestSplit(GenericCSVDataset):
    def __init__(self, **kwargs):
        super().__init__(kwargs)
        self.name = 'ZINC15 Test Split 20K Samples'
        self.table_name = 'zinc15_test'
        self.properties_cols = ['logp', 'mw']
        self.index_col = 'index'
        self.data_path = os.path.join(pathlib.Path(__file__).parent.parent.absolute(),
                                      'data',
                                      'benchmark_ZINC15_test_split.csv')
        assert os.path.exists(self.data_path)

    def load(self, columns=['canonical_smiles'], length_column='length'):
        self.data, _ = self._load_csv(columns, length_column, return_remaining=False)


### DEPRECATED ###
class ChEMBL20KSamples(GenericCSVDataset):
    def __init__(self, **kwargs):
        super().__init__(kwargs)
        self.name = 'ChEMBL 20K Samples'
        logger.warn(f'Class {self.name} is deprecated.')
        self.index_col = 'molregno'
        self.data_path = os.path.join(pathlib.Path(__file__).parent.parent.absolute(),
                                      'data',
                                      'benchmark_ChEMBL_random_sampled_drugs.csv')
        assert os.path.exists(self.data_path)