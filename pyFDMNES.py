# -*- coding: utf-8 -*-
"""
Created on Thu Jul 25 17:03:33 2013

@author: weiget
"""

import numpy as np
import StringIO
import logging
import os
import elements
import subprocess
import string


flags = ["Green","Magnetism", "Density","Self-absorption","cartesian",
         "nodipole"] 
         
conv_flags = ["Gamma_fix", "Fprime", "Fprime_atom", "Estart","Efermi"]

SCF_flags = ["N_self","P_self","R_self", "Delta_E_conv", "SCF_exc",
             "SCF_mag_free"]
        
Multi_Exp_flags = ["Quadrupole","Octupole","Dimag", "E1E2","E1E3","E2E2","E3E3",
                   "E1M1","M1M1","No_E1E1","No_E2E2","No_E1E2","No_E1E3"]

EXEfile = os.path.abspath('\\\\win.desy.de\\home\\weiget\\My Documents\\fdmnes_2013_05_27\\fdmnes\\fdmnes.exe')

def array2str(array, precision=4):
    array = np.array(array)
    if array.ndim<2:
            array = array[:,np.newaxis].T
    if array.dtype == int:
        zahl = "%i "
    elif array.dtype == float:
        zahl = "%." + str(int(precision)) + "f " 
    save_value = StringIO.StringIO()
    np.savetxt(save_value, array, fmt = zahl)   
    values = save_value.getvalue()
    return values


class pyFDMNES(object):
    
    def __init__(self, structure, resonant="", verbose=False):
        """
            Initializes the crystals unit cell for a given
            structure in the following steps:
                - retrieve space group generators for the given space group
                - calculate real and reciprocal lattice parameters
                - calculates Matrices B, B_0
                - calculates real and reciprocal metric tensors G, G_r

            Optionally loads a structure from a .cif file.
            See:
                Hall SR, Allen FH, Brown ID (1991).
                "The Crystallographic Information File (CIF):(dafs[:,0], dafs[:,y1], label = "")
                 a new standard archive file for crystallography".
                Acta Crystallographica A47 (6): 655-685
            A list or string of 'resonant' scattering atoms can be given.
            
            
            Input parameters:
                structure : either
                                - metric (cell dimensions) of the crystal
                            or
                                - path to .cif-file
        """
        self.positions = {} # symmetric unit
        self.elements = {}
        self.verbose = verbose
        self.resonant = []
        self.atom_num = {}
        self.occupancy = {}
        self.Crystal = True
        self.Radius = 2.5
        self.Range = "-10. 0.1 -2 0.2 0. 0.5 20. 1. 40."
        self.Polarise = []
        self.Reflex = []
        self.Atom = {}
        self.dafs = []
        self.Rpotmax = 0
        self.Run_File = 2
        self.extract = False
        self.Absorber = ()
        self.convolution = False
        self.Efermi = 0
        self.Estart = 0
        
        if str(structure).isdigit():
            int(structure)
            self.a, self.b, self.c, self.alpha, self.beta, self.gamma = structure
            self.cif = False
        elif os.path.isfile(structure):
             end = os.path.splitext(structure)[1].lower()
             if end == ".cif":
                 self.load_cif(structure, resonant)
             elif end == ".txt":
                 self.Filein(structure)
        
    
    def add_atom(self, label, position, occupancy=1):
        """
            Method to fill the asymmetric unit with atoms.
            
            Inputs:
            -------
                label : string
                    The label of the atom.
                    It has to be unique and to start with the symbold of the
                    chemical element.
                position : iterable of length 3
                    Position of the atom in the basis of the lattice vectors.
                isotropic : bool
                    Defines whether the atom is an isotropic scatterer which
                    is mostly the case far from absorption edges.
                assume_complex : bool
                    Defines whether the scalar atomic scattering amplitude shall
                    be assumed to be complex. This can be left False, since the
                    calculations are symbolic and values, that will be entered
                    later, still can be complex.
                dE : scalar
                    Sets the shift of the absorption edge for this particular
                    atom.
        """
        if type(label) is not str: raise TypeError("Invalid label. Need string.")
        if len(position) is not 3: raise TypeError("Enter 3D position object!")
        
        position = np.array(position)
        #label = label.replace("_", "")
        labeltest = label[0].upper()
        if len(label) > 1:
            labeltest += label[1].lower()
        if labeltest in elements.Z.keys():
            self.elements[label] = labeltest
        elif labeltest[:1] in elements.Z.keys():
            self.elements[label] = labeltest[:1]
        else:
            raise ValueError("Atom label shall start with the symbol of the chemical element" + \
                             "Chemical element not found in %s"%label)                    
    
        self.atom_num[label] = elements.Z[self.elements[label]]
        self.occupancy[label] = occupancy
        self.positions[label] = position
        
    def load_cif(self, fname, resonant=""):
        """
            Loads a structure from a .cif file.
            See:
                Hall SR, Allen FH, Brown ID (1991).
                "The Crystallographic Information File (CIF): a new standard 
                archive file for crystallography".
                Acta Crystallographica A47 (6): 655-685
            
            A list or string of resonant scattering atoms can be given.
            
        """
        fobject = open(fname, "r")
        lines = fobject.readlines()
        fobject.close()
        lines.reverse()
        num_atom = 0
        while lines:
            Line = lines.pop()
            Line = Line.replace("\t", " ")
            line = Line.lower()
            if line.startswith("_symmetry_int_tables_number"):
                self.sg_num = int(Line.split()[1])
            elif line.startswith("_symmetry_space_group_name_h-m"):
                self.sg_name = Line.split("'")[1].replace(" ","")
                if ":" in self.sg_name:
                    self.cscode = ":" + self.sg_name.split(':')[1]
            elif line.startswith("_cell_length_a"):
                self.a = float(Line.split()[1].partition("(")[0]) #)
            elif line.startswith("_cell_length_b"):
                self.b = float(Line.split()[1].partition("(")[0]) #)
            elif line.startswith("_cell_length_c"):
                self.c = float(Line.split()[1].partition("(")[0]) #)
            elif line.startswith("_cell_angle_alpha"):
                self.alpha = float(Line.split()[1].partition("(")[0]) #)
            elif line.startswith("_cell_angle_beta"):
                self.beta = float(Line.split()[1].partition("(")[0]) #)
            elif line.startswith("_cell_angle_gamma"):
                self.gamma = float(Line.split()[1].partition("(")[0]) #)
            elif line.startswith("_atom_site"):
                if line.startswith("_atom_site_label"): col_label = num_atom
                elif line.startswith("_atom_site_type_symbol"): col_symbol = num_atom
                elif line.startswith("_atom_site_fract_x"): col_x = num_atom
                elif line.startswith("_atom_site_fract_y"): col_y = num_atom
                elif line.startswith("_atom_site_fract_z"): col_z = num_atom
                num_atom+=1
            elif num_atom>0 and len(Line.split())==num_atom:
                atomline = Line.split()
                label = atomline[col_label]
                symbol = atomline[col_symbol]
                if symbol[:2].isalpha(): 
                   symbol = symbol[:2]
                else: symbol = symbol[:1]
                if symbol==resonant:
                    self.resonant.append(label)
                px = float(atomline[col_x].partition("(")[0]) #)
                py = float(atomline[col_y].partition("(")[0]) #)
                pz = float(atomline[col_z].partition("(")[0]) #)
                position = (px, py, pz)       
                if logging.DEBUG: 
                    self.add_atom(label, position)


    def Filout(self, path):
        
        self.path = path
        
       # if os.path.exists(path):
            # print ("path exist!")
            # return
        
        try: f = open(path, "w")
        except IOError:
            print "Error: No new file open"
        
        else: 
            print "Written content in the file successfully"
            
            if "_inp" in path:
                path_part = os.path.splitext(path)[0]
                self.new_name = path_part.replace("_inp","_out")
                self.new_path = os.path.relpath(self.new_name, os.path.dirname(EXEfile))
                f.write("Filout \n %s \n\n" %self.new_path)
            else:
                path_basename = os.path.splitext(path)[0]
                self.new_name = path_basename + "_out"
                self.new_path = os.path.relpath(self.new_name, os.path.dirname(EXEfile))
                f.write("Filout \n %s \n\n" %self.new_path)
            
            if self.extract == False:
                self.bav = self.new_name + "_bav.txt"

        #if hasattr(self, "Range"):
            if isinstance(self.Range, str) and not self.extract:
                f.write("Range \n %s \n\n" % self.Range)
        
        #if self.radius == isinstance (float):
            if isinstance(self.Radius, float) and not self.extract:
                f.write("Radius \n %f \n" % self.Radius)
            
            if self.Rpotmax != 0 and not self.extract:
                f.write("\nRpotmax \n %s\n" %self.Rpotmax)
        
            for key in flags:
                if hasattr(self,key) and getattr(self,key) ==True:
                        f.write("\n%s \n" %key)
              
            for key in Multi_Exp_flags :
                 if hasattr(self,key) and getattr(self,key)==True:
                     f.write("\n%s \n" %key)
            
                #if getattr(self,key) == True:
            if hasattr(self, "SCF") and self.SCF and not self.extract:
                f.write("\nSCF \n")
                for key in SCF_flags:
                    if hasattr(self, key):
                        value = getattr(self, key)
                        if isinstance(value, bool):
                            f.write("%s \n" %key)
                        else:
                            f.write("%s \n %f \n" %(key, getattr(self, key))) 
                
            f.write("\nSpgroup \n %i" %self.sg_num)
            if hasattr(self,"cscode"):
                f.write("%s\n\n" %self.cscode)
            else:f.write("\n\n")
                
            if hasattr(self,"Absorber") and len(self.Absorber)>0:
                f.write("Absorber\n %s \n\n" %self.Absorber)

            if hasattr(self, "Atom") and len(self.Atom)>0:
                f.write("Atom\n")
                #if isinstance(self.Atom, dict):
                for label in self.Atom.keys():
                    f.write(" %i" %self.atom_num[label])
                    atm_conf = array2str(self.Atom[label])
                    f.write(" %s" %atm_conf)
                
            if self.Crystal == True: f.write("\nCrystal \n") 
            else: f.write("Molecule \n")
            
            cell = (self.a, self.b, self.c, self.alpha, self.beta, self.gamma)
            f.write("   %f %f %f %f %f %f\n" %cell)
                                                               
            for label in self.resonant:
                if len(self.Atom)>0:
                    num = self.Atom.keys().index(label) + 1
                    f.write(" %i " %num)
                else:
                    f.write(" %i " %self.atom_num[label])
                atm_pos = array2str(self.positions[label])
                f.write("%s" %atm_pos)
                 
            for label in self.positions.iterkeys():
                if label in self.resonant:
                    pass
                else:
                    if len(self.Atom)>0:
                        num = self.Atom.keys().index(label) + 1
                        f.write(" %i " %num)
                    else:
                        f.write(" %i " %self.atom_num[label])
                    atm_pos = array2str(self.positions[label])
                    f.write("%s" %atm_pos)
    
            if self.extract == True and os.path.exists(self.bav):
                bav_file = os.path.abspath(self.bav)
                f.write("\nextract\n %s\n" %bav_file)
                
                if hasattr(self,"ext_Absorber") and len(self.ext_Absorber)>0:
                    f.write("Absorber\n%s \n\n" %self.ext_Absorber)
                    f.write("Extractpos\n%s \n\n"%self.Absorber)
                    
                if hasattr(self,"Rotsup") and len(self.Rotsup)>0:
                   f.write("Rotsup\n%s \n\n" %self.Rotsup)
                
                if hasattr(self,"Extractsym") and len(self.Extractsym)>0:
                   f.write("Extractsym\n%s \n\n" %self.Extractsym)
                 
                if hasattr(self,"Reflex") and len(self.Reflex)>0: 
                    Reflex_val = array2str(self.Reflex, precision=0)
                    f.write("\nRXS\n%s\n" %Reflex_val)
                
                if hasattr(self,"Polarise") and len(self.Polarise)>0:
                    Polarise_val = array2str(self.Polarise)
                    f.write("\nPolarise\n%s\n" %Polarise_val)
                    
                if hasattr(self,"dafs") and len(self.dafs)>0:
                    dafs_val = array2str(self.dafs)
                    f.write("\nAtom\n%s \n" %dafs_val)

            if self.convolution == True: 
                if self.Efermi != 0: 
                   f.write("Efermi \n %f\n\n" %self.Efermi)
                
                if self.Estart != 0: 
                    f.write("EStart \n %f\n\n" %self.Estart)
                
            f.write("\nConvolution \n\nEnd")
    
       # if self.R_self != self.Radius: oder 3.5???
            # f.write("...")
       #if self.N_self != 30:
            #f.write("...")

        finally:
                f.close()
            
    def FDMNESfile (self):
        
        assert hasattr(self, "path"), "Attribute `path` has not been defined. Try self.Filout() first"
        self.workdir = os.getcwd()
        
        File = os.path.split(EXEfile)
        fdmfile =os.path.join(File[0],"fdmfile.txt")
        
        
        Input = os.path.relpath(self.path, os.path.dirname(EXEfile))
        #Input = os.path.relpath(self.path, os.getcwd())
        
        try: f = open(fdmfile,"w")
        except IOError:
            print "Error: fdmfile not open"
        
        else: 
            print "Written fdmfile was successfully"
            
            if self.convolution == True:
                self.Run_File = 1
                f.write("\n%i\n\n%s\n" %(self.Run_File,Input))
            else:
                Input_conv = os.path.relpath(self.conv_path, os.path.dirname(EXEfile))
                f.write("\n%i\n\n%s\n%s\n" %(self.Run_File,Input,Input_conv))
        
        finally: 
            f.close()
        
        os.chdir(File[0])
        logfile = open(os.path.join(self.workdir, "fdmnfile.txt"), "w")
        #errfile = open(os.path.join(self.workdir, "fdmnes_error.txt", "w"))
        if self.verbose:
            stdout = None
        else:
            stdout = logfile
        try:
            self.proc = subprocess.Popen(EXEfile, stdout=stdout) #stderr = errfile)
            self.proc.wait()
            print("FDMNES simulation finished")
        except:
            pass
        finally:
            logfile.close()
        os.chdir(self.workdir)
        
    def retrieve (self):
        if (not hasattr(self, "proc") or self.proc.poll() != None) and os.path.exists(self.bav):
            bav_open  = open(self.bav)
            line = bav_open.readlines()
            if ("Have a beautiful day !") in line[-1]:
                print("Process was sucessfully")
        else: print("Process wasn't sucessfully")
            
            
    def Filein (self, fname):
        fobject = open(fname, "r")
        content = fobject.read()
        fobject.close()
        
        content_red = map(string.strip,content.splitlines())
        content_red = filter(lambda x: x is not "", content_red)
        
        keywords = ["Convolution", "SCF", "SCF_exc", "SCF_mag_free"]
        keywords_float = ["Radius", "Efermie", "Estart","Rpotmax",
                          "N_self","P_self","R_self", "Delta_E_conv",]
        keywords_int = ["Absorber"]
                
        self.new_name = os.path.splitext(fname)[0].replace("_inp","_out")
        self.bav = self.new_name + "_bav.txt"

        if "Range" in content_red:
                self.Range = content_red[content_red.index("Range")+1]
                
        for line in content_red:
            if line in flags + Multi_Exp_flags + keywords:
                 setattr(self, line, True)
            
            if line in keywords_float:
                setattr(self, line, float(content_red[content_red.index(line)+1]))
                
            if line in keywords_int:
                setattr(self, line, int(content_red[content_red.index(line)+1]))
                
            if line == "Spgroup":
                line = content_red[content_red.index(line)+1]
                if ":" in line:
                    line.split(':')
                    self.sg_num = int(line[0])
                    self.cscode = ":" + line[1]
                else:
                    self.sg_num = int(line)
                
            if line == "Atom":
                Atom = []
                linenum = content_red.index(line)
                atom_num_list = []
                while True:
                    try: 
                        linenum += 1
                        atomline = content_red[linenum]
                        atomline = atomline.split()
                        atomline = map(float, atomline)
                        atom_num = int(atomline[0])
                        atom_num_list.append(atom_num)
                        anzahl = atom_num_list.count(atom_num)
                        symbol = elements.symbols[atom_num] + str(anzahl)
                        atm_conf = atomline[1:]
                        Atom.append((symbol,atm_conf))
                    except ValueError:
                        break
               # while :
                #    self.atm_conf = content_red[content_red.index(line)+1]
                
            if line in ["Crystal", "Molecule"]:
                if line=="Crystal":
                    self.crystal=True
                linenum = content_red.index(line)+1
                cellline = content_red[linenum]
                cellline = cellline.split()
                cellline = map(float, cellline)
                self.a, self.b, self.c, self.alpha, self.beta, self.gamma = cellline
                positions = []
                while True:
                    try: 
                        linenum += 1
                        atomline = content_red[linenum]
                        atomline = atomline.split()
                        atomline = map(float, atomline)
                        num = int(atomline[0])
                        position = atomline[1:4]
                        positions.append((num, position))
                    except ValueError:
                        break
        
        self.positions = {}
        self.atom_num = {}
        for atom in positions:
            num = atom[0]
            position = atom[1:]
            symbols = []
            if "Atom" in content_red:
                symbol = Atom[num-1][0]
                self.atom_num[symbol] = elements.Z[symbol[:-1]]
            else:
                symbol = elements.symbols[num]
                self.atom_num[symbol] = elements.Z[symbol]
                symbols.append(symbol)
                anzahl = symbols.count(symbol)
                symbol += str(anzahl)
            
            self.positions[symbol] = position 
        self.Atom = dict(Atom)
                            
       #         self.Crysatal = line
        #        self.cell = content_red[content_red.index(line)+1]
         #       while 
                
                                  
        #return content_red

    def get_XANES(self, conv = True):
        """
            was macht get_XANES???
        """
        if conv == True:
            fname = self.new_name + "_conv.txt"
            skiprows = 1
        else:
            fname = self.new_name + ".txt"
            skiprows = 4
        
        data = np.loadtxt(fname, skiprows = skiprows)
        return data
        
        
    def get_dafs (self, Reflex, pol_in, pol_out, azimuth, conv = True):
        
        self.Reflex = self.Reflex.round(0)
        
       
        if conv == True:
            fname = os.path.abspath(self.new_name) + "_conv.txt"  
            skiprows = 1  
            a = 0

        else:
            fname = os.path.abspath(self.new_name) + ".txt"
            skiprows = 4
            a = 3
                   
        fobject = open(fname,"r") 
        lines = fobject.readlines()
        fobject.close()
        headline = lines[a]
        headline_keywords = headline.split()
            
        Reflex_a = np.array(Reflex)
        if np.ndim(self.Reflex)>1:
            columns = (self.Reflex[:,0:3] == Reflex).all(1)
        
            if pol_in != None:
                col_pol_in = (self.Reflex[:,3] == pol_in)
                columns *= col_pol_in
            if pol_out != None:
                col_pol_out = (self.Reflex[:,4] == pol_out)
                columns *= col_pol_out
            if azimuth != None:
                col_azimuth = (self.Reflex[:,5].round(0) == np.round(azimuth))
                columns *= col_azimuth
                
        else:
            columns = (self.Reflex[0:3] == Reflex).all(0)
            
            col_pol_in = (self.Reflex[3] == pol_in)
            columns *= col_pol_in
            
            col_pol_out = (self.Reflex[4] == pol_out)
            columns *= col_pol_out
            
            col_azimuth = (self.Reflex[5].round(0) == np.round(azimuth))
            columns *= col_azimuth
            
        columns_a = np.where(columns)[0]
        
        if len(columns_a) == 0:
            Reflex_new = np.append(Reflex_a, np.array([pol_out, pol_in, azimuth]))
            self.Reflex = Reflex_new
            return self.Reflex

        else:
            if conv == True:
                self.column = columns_a+2
                self.index = headline_keywords[self.column]
            else:
                column = (2*columns_a+2)
                index = headline_keywords[column]
                index_a = index.replace("r","I")
                self.index = index_a+" without convolution"
                
                self.column_real = column
                self.index_real = headline_keywords[self.column_real]
                
                self.column_im = column + 1
                self.index_im = headline_keywords[self.column_im]

            
        dafs = np.loadtxt(fname, skiprows = skiprows)
        return dafs
        
    def do_convolution(self, path):
        
        self.conv_path = os.path.realpath(path)
    
        try: f = open(path, "w")
        except IOError:
            print "Error: No new file open"
        
        else: 
            print "Written content in the file successfully"
            
            f.write("Calculation \n")
            filout = self.new_path + ".txt"
            f.write("%s \n\n" %filout)
            
     #       if self.scan = True:
     #           self.scan = self.new_path + "_scan.txt"
     #           f.write("Scan \n %s\n\n" %scan)

            scan_conv = self.new_path + "_scan_conv.txt"
            f.write("Scan_conv \n %s\n\n" %scan_conv)
            
            f.write("Convolution \n\n")
            
            f.write("check_conv\n\n")
        
            for key in conv_flags:
                if hasattr(self,key):
                    value =  getattr(self,key)
                    if isinstance(value, bool):
                        f.write("%s \n" %key)
                    else:
                        f.write("%s \n %f \n" %(key, getattr(self, key))) 

            f.write("\nEnd")
                
        finally: 
                f.close()
        