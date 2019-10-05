from rdkit import Chem
from rdkit.Chem import AllChem
# from Per_Frame_Property_Extractor import *
from .Extractor import *

from numpy import mean, std, median
import functools

class MDFP():
    """
    .. todo::
        - method to give back the keys
        - store some metdadata?
    """
    def __init__(self, dict):
        self.fp = dict

    def get_mdfp(self):
        """
        Returns
        ----------
        a list of floating values, i.e. the mdfp feature vector
        """
        return functools.reduce(lambda a, b : a + b, self.fp.values())

class BaseComposer():
    """
    The BaseComposer class containing functions that can be used by different composers for different types of simulations

    """

    @classmethod
    def run(cls, smiles ):
        """
        Parameters
        ----------
        smiles : str
            SMILES string of the solute molecule
        """
        cls.smiles = smiles
        cls.fp = {}
        cls._get_relevant_properties()

        return MDFP(cls.fp)

    @classmethod
    def _get_relevant_properties(cls):
        """
        Parameters
        ----------

        smiles : str
            SMILES string of the solute molecule
        """
        cls.fp  = {**cls.fp, **cls._get_2d_descriptors()}

    @classmethod
    def _get_2d_descriptors(cls):
        """
        Parameters
        ----------

        smiles : str
            SMILES string of the solute molecule
        """
        m = Chem.MolFromSmiles(cls.smiles, sanitize = True)
        if m is None:
            m = Chem.MolFromSmiles(cls.smiles, sanitize = False)
            m.UpdatePropertyCache(strict=False)
            Chem.GetSSSR(m)

        fp = []
        fp.append(m.GetNumHeavyAtoms())
        fp.append(AllChem.CalcNumRotatableBonds(m))
        fp.append(len(m.GetSubstructMatches(Chem.MolFromSmarts('[#7]')))) # nitrogens
        fp.append(len(m.GetSubstructMatches(Chem.MolFromSmarts('[#8]')))) # oxygens
        fp.append(len(m.GetSubstructMatches(Chem.MolFromSmarts('[#9]')))) # fluorines
        fp.append(len(m.GetSubstructMatches(Chem.MolFromSmarts('[#15]')))) # phosphorous
        fp.append(len(m.GetSubstructMatches(Chem.MolFromSmarts('[#16]')))) # sulfurs
        fp.append(len(m.GetSubstructMatches(Chem.MolFromSmarts('[#17]')))) # chlorines
        fp.append(len(m.GetSubstructMatches(Chem.MolFromSmarts('[#35]')))) # bromines
        fp.append(len(m.GetSubstructMatches(Chem.MolFromSmarts('[#53]')))) # iodines
        return {"2d_counts" : fp}


    @classmethod
    def _get_statistical_moments(cls, property_extractor, statistical_moments = [mean, std, median], **kwargs):
        """
        Parameters
        ----------

        smiles : str
            SMILES string of the solute molecule
        """
        cls.statistical_moments = [i.__name__ for i in statistical_moments]
        fp = {}
        prop = property_extractor(**kwargs)
        for i in prop:
            fp[i] = []
            for func in statistical_moments:
                 fp[i].append(func(prop[i]))
        return fp

"""
class TrialSolutionComposer(BaseComposer):
    def __init__(cls, smiles, mdtraj_obj, parmed_obj, **kwargs):
        cls.kwargs = {"mdtraj_obj" : mdtraj_obj ,
                        "parmed_obj" : parmed_obj}
        cls.kwargs = {**cls.kwargs , **kwargs}
        super(TrialSolutionComposer, cls).__init__(smiles)
    def _get_relevant_properties(cls):
        cls.fp  = {**cls.fp, **cls._get_2d_descriptors()}
        cls.fp  = {**cls.fp, **cls._get_statistical_moments(TrialSolutionExtractor.extract_energies, **cls.kwargs)}
        cls.fp  = {**cls.fp, **cls._get_statistical_moments(WaterExtractor.extract_rgyr, **cls.kwargs)}
        cls.fp  = {**cls.fp, **cls._get_statistical_moments(WaterExtractor.extract_sasa, **cls.kwargs)}

        del cls.kwargs
"""

# class MDFPComposer(BaseComposer):
class SolutionComposer(BaseComposer):
    """
    Generates fingerprint most akin to that from the original publication
    """
    @classmethod
    def run(cls, mdtraj_obj, parmed_obj, smiles = None, **kwargs):
        cls.kwargs = {"mdtraj_obj" : mdtraj_obj ,
                        "parmed_obj" : parmed_obj}
        cls.kwargs = {**cls.kwargs , **kwargs}
        if smiles is None:
            if parmed_obj.title != '': #try to obtain it from `parmed_obj`
                smiles = parmed_obj.title
            else:
                raise ValueError("Input ParMed Object does not contain SMILES string, add SMILES as an additional variable")
        else:
            return super().run(smiles)

    @classmethod
    def _get_relevant_properties(cls):
        cls.fp  = {**cls.fp, **cls._get_2d_descriptors()}
        cls.fp  = {**cls.fp, **cls._get_statistical_moments(WaterExtractor.extract_energies, **cls.kwargs)}
        cls.fp  = {**cls.fp, **cls._get_statistical_moments(WaterExtractor.extract_rgyr, **cls.kwargs)}
        cls.fp  = {**cls.fp, **cls._get_statistical_moments(WaterExtractor.extract_sasa, **cls.kwargs)}
        del cls.kwargs

class LiquidComposer(BaseComposer):
    # def __init__(cls, smiles, mdtraj_obj, parmed_obj):
    @classmethod
    def run(cls, mdtraj_obj, parmed_obj, smiles = None, **kwargs):
        cls.kwargs = {"mdtraj_obj" : mdtraj_obj ,
                        "parmed_obj" : parmed_obj}
        cls.kwargs = {**cls.kwargs , **kwargs}
        if smiles is None:
            if parmed_obj.title != '': #try to obtain it from `parmed_obj`
                smiles = parmed_obj.title
            else:
                raise ValueError("Input ParMed Object does not contain SMILES string, add SMILES as an additional variable")
        else:
            return super().run(smiles)

    @classmethod
    def _get_relevant_properties(cls):
        cls.fp  = {**cls.fp, **cls._get_2d_descriptors()}
        cls.fp  = {**cls.fp, **cls._get_statistical_moments(LiquidExtractor.extract_energies, **cls.kwargs)}
        cls.fp  = {**cls.fp, **cls._get_statistical_moments(LiquidExtractor.extract_rgyr, **cls.kwargs)}
        cls.fp  = {**cls.fp, **cls._get_statistical_moments(LiquidExtractor.extract_sasa, **cls.kwargs)}
        cls.fp  = {**cls.fp, **cls._get_statistical_moments(LiquidExtractor.extract_dipole_magnitude, **cls.kwargs)}

        del cls.kwargs

class SolutionLiquidComposer(BaseComposer):
    @classmethod
    def __init__(cls, solv_mdtraj_obj, solv_parmed_obj, liq_mdtraj_obj, liq_parmed_obj, smiles = None, **kwargs):
        cls.kwargs_solv = {"mdtraj_obj" : solv_mdtraj_obj ,
                        "parmed_obj" : solv_parmed_obj}
        cls.kwargs_liq = {"mdtraj_obj" : liq_mdtraj_obj ,
                        "parmed_obj" : liq_parmed_obj}
        cls.kwargs_liq = {**cls.kwargs_liq , **kwargs}
        cls.kwargs_solv = {**cls.kwargs_solv , **kwargs}

        if smiles is None:
            if parmed_obj.title != '': #try to obtain it from `parmed_obj`
                smiles = parmed_obj.title
            else:
                raise ValueError("Input ParMed Object does not contain SMILES string, add SMILES as an additional variable")
        else:
            return super().run(smiles)

    @classmethod
    def _get_relevant_properties(cls):
        cls.fp  = {**cls.fp, **cls._get_2d_descriptors()}

        cls.fp  = {**cls.fp, **cls._get_statistical_moments(WaterExtractor.extract_energies, **cls.kwargs_solv)}
        cls.fp  = {**cls.fp, **cls._get_statistical_moments(WaterExtractor.extract_rgyr, **cls.kwargs_solv)}
        cls.fp  = {**cls.fp, **cls._get_statistical_moments(WaterExtractor.extract_sasa, **cls.kwargs_solv)}

        cls.fp  = {**cls.fp, **cls._get_statistical_moments(LiquidExtractor.extract_energies, **cls.kwargs_liq)}
        cls.fp  = {**cls.fp, **cls._get_statistical_moments(LiquidExtractor.extract_rgyr, **cls.kwargs_liq)}
        cls.fp  = {**cls.fp, **cls._get_statistical_moments(LiquidExtractor.extract_sasa, **cls.kwargs_liq)}
        cls.fp  = {**cls.fp, **cls._get_statistical_moments(LiquidExtractor.extract_dipole_magnitude, **cls.kwargs_liq)}

        del cls.kwargs_liq, cls.kwargs_solv

"""
parm_path = '/home/shuwang/Documents/Modelling/MDFP/Codes/vapour_pressure/crc_handbook/corrupted/RU18.1_8645.pickle'
parm = pickle.load(open(parm_path,"rb"))
traj = md.load('/home/shuwang/Documents/Modelling/MDFP/Codes/vapour_pressure/crc_handbook/corrupted/RU18.1_8645.h5')[:10]
# print(Liquid_Extractor.extract_dipole_magnitude(traj, parm))
x = MDFPComposer("Cl-C1:C:C:C:C2:C:C:C:C:C:1:2", traj, parm)
# print(x._get_statistical_moments(Base_Extractor.extract_rgyr, **{"mdtraj_obj" : traj}))
# print(x._get_statistical_moments(Liquid_Extractor.extract_dipole_magnitude, **{"mdtraj_obj" : traj, "parmed_obj" : parm}))
# print(x._get_statistical_moments(Base_Extractor.extract_sasa, **{"mdtraj_obj" : traj, "parmed_obj" : parm}))
# print(x._get_statistical_moments(Liquid_Extractor.extract_energies, **{"mdtraj_obj" : traj, "parmed_obj" : parm , "platform" : "OpenCL"}))
print(x.fp)
print(x.__dict__)
print(x.get_mdfp())
pickle.dump(x, open("/home/shuwang/tmp.pickle", "wb"))
"""
