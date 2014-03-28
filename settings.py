from collections import namedtuple

nan = float("nan")

ParamTypes = namedtuple("ParamTypes", ("Basic", 
                                       "SCF", 
                                       "Multipole",
                                       "RXS",
                                       "Spin",
                                       "Convolution", 
                                       "Extract", 
                                       "Experiment"))

Defaults = ParamTypes({}, {}, {}, {}, {}, {}, {}, {})

Defaults.SCF['Delta_E_conv'] = 1.
Defaults.SCF['N_self'] = 30
Defaults.SCF['P_self'] = 0.1
Defaults.SCF['R_self'] = 0.
Defaults.SCF['SCF'] = False
Defaults.SCF['SCF_exc'] = False
Defaults.SCF['SCF_mag_free'] = False

Defaults.Basic["Absorber"] = ()
Defaults.Basic["Atom"] = []
Defaults.Basic["Atom_conf"] = []
Defaults.Basic["Cartesian"] = False
Defaults.Basic["Density"] = False
Defaults.Basic["Edge"] = "K"
Defaults.Basic["Energpho"] = False
Defaults.Basic["Green"] = False
Defaults.Basic["Hubbard"] = 0.
Defaults.Basic["Magnetism"] = False
Defaults.Basic["Memory_save"] = False
Defaults.Basic["Polarize"] = []
Defaults.Basic["Radius"] = 5.67
Defaults.Basic["Range"] = (-5., 0.5, 60.) # eV with respect to edge
Defaults.Basic["Relativism"] = False
Defaults.Basic["Rpotmax"] = 0.
Defaults.Basic["TDDFT"] = False
Defaults.Basic["RPA"] = False
Defaults.Basic["Z_absorber"] = 0

Defaults.Multipole['Dipmag'] = False
Defaults.Multipole['E1E2'] =  False
Defaults.Multipole['E1E3'] =  False
Defaults.Multipole['E1M1'] =  False
Defaults.Multipole['E2E2'] =  False
Defaults.Multipole['E3E3'] =  False
Defaults.Multipole['M1M1'] =  False
Defaults.Multipole['No_E1E1'] =  False
Defaults.Multipole['No_E1E2'] =  False
Defaults.Multipole['No_E1E3'] =  False
Defaults.Multipole['No_E2E2'] =  False
Defaults.Multipole['Octupole'] =  False
Defaults.Multipole['Quadrupole'] =  False

Defaults.RXS['Azimuth'] = []
Defaults.RXS['Circular'] = False
Defaults.RXS['Dead_layer'] = 0.
Defaults.RXS['Double_cor'] = False
Defaults.RXS['Full_self_abs'] = False
Defaults.RXS['Polarization'] = []
Defaults.RXS['Reflection'] = []
Defaults.RXS['Self_abs'] = False
Defaults.RXS['Step_azim'] = 2.
Defaults.RXS['Zero_azim'] = (0.,0.,0.) # 3-tuple float

Defaults.Spin["Axe_spin"] = (0.,0.,1.) # 3-tuple float
Defaults.Spin["Ang_spin"] = (0.,0.,0.) # 3-tuple float
Defaults.Spin["Magnetism"] = False
Defaults.Spin["Nonrelat"] = False
Defaults.Spin["Spinorbite"] = False

Defaults.Convolution["Calculation"] = []
Defaults.Convolution["Check_conv"] = False
Defaults.Convolution["Convolution"] = False
Defaults.Convolution["Conv_out"] = ""
Defaults.Convolution["Dec"] = False
Defaults.Convolution["Ecent"] = 30. 
Defaults.Convolution["Efermi"] = -5. 
Defaults.Convolution["Elarg"] = 30. 
Defaults.Convolution["Estart"] = nan 
Defaults.Convolution["Forbidden"] = False 
Defaults.Convolution["Fprime"] = False 
Defaults.Convolution["Fprime_atom"] = False 
#Defaults.Convolution["Gamma_fix"] = False # obsolete, use Gamma_var instead
Defaults.Convolution["Gamma_hole"] = -1. 
Defaults.Convolution["Gamma_max"] = 15. 
Defaults.Convolution["Gamma_var"] = False 
Defaults.Convolution["Gaussian"] = 0. 
Defaults.Convolution["Nocut"] = False
Defaults.Convolution["Photoemission"] = False
Defaults.Convolution["S0_2"] = 1.
Defaults.Convolution["Scan"] = [] 
Defaults.Convolution["Scan_conv"] = ""
Defaults.Convolution["Seah"] = [0., 0.] 
Defaults.Convolution["Selec_core"] = -1
Defaults.Convolution["Thomson"] = nan

# To be considered later:
Defaults.Extract["Extract"] = ""
Defaults.Extract["Extractpos"] = []
Defaults.Extract["Extractsym"] = []
Defaults.Extract["Rotsup"] = []


Defaults.Experiment["Gen_shift"] = [0.,0.,0]
Defaults.Experiment["Emin"] = nan
Defaults.Experiment["Emax"] = nan
Defaults.Experiment["Kev"] = False




