import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET
import os
import string
from pathlib import Path
from plotter import plotter

# sys.tracebacklimit = 0

# ######################################
# ######################################
# ######################################
# ###################################### USER BOX
# path         = '/scratch/rguerrero'+'/'   #path where the python code is 
# file1        = path+'vasprun_rodrigo.xml'  #path where the vasprun is
# outfile      = 'vasprun_rodrigo'       #the name of the image do you want
# # hsp_labels   = [r'$\Gamma$','M','K',r'$\Gamma$']  #high symmetry point 
# hsp_labels   = ['G','M','K','G']  #high symmetry point 
# context      = 'normal'
# orbital      = None
# atom         = 6
# ylims = (-5,5)
# ######################################
# ######################################
# hsp_labels = [r'$\Gamma$' if 'G' in i else i for i in hsp_labels]
# ######################################
# ######################################

# root = ET.parse(infile).getroot()

class bands_df:
    """ """
    def __init__(self,infile):
        self.infile = infile
        self.path = '/'.join(self.infile.split('/')[:-1])+'/'
        self.route = self.path+'bands.csv'
        if os.path.isfile(self.route):
            print(self.route,'exists')
            self.indi = True
        else:
            self.raiz   = ET.parse(infile).getroot()
            self.indi   = False
    
    def eigh(self,plot=False,band_index='all',hsp_names=[],ylim=(None,None),title='',marker='',dpi=300,xhsp=[],xshift=50):
        """

        Parameters
        ----------
        plot :
            (Default value = False)
        band_index :
            (Default value = 'all')
        hsp_names :
            (Default value = [] (an empty list))
        ylim :
            (Default value = (None)
        None) :
            
        title :
            (Default value = '')
        marker :
            (Default value = '')
        dpi :
            (Default value = 300 (the resolution of the png file))
        xhsp :
            (Default value = [] (if none list of strings  is entered the code will provide an alphanetic list, i.e., [a,b,c,d].))
        xshift :
            (Default value = 50 <integer value> (xshift is very useful when plotting around one single HSP point and zoom around that point by xshift. 
            Note that xshift is the number of index not real values))

        Returns
        -------

        
        """
        if self.indi == False:
            # THIS IS the file path!
            
            #Kpoint path
            pathinfo  = [  np.array(vv.text.split(),dtype=float) for vv in self.raiz.findall("./kpoints/generation/*")]
            divisions = int(pathinfo[0][0])  #separation between paths
            npaths    = len(pathinfo[1:]) #number of paths sections
            hsp_index = [i * divisions  for i in range(npaths)]
            ##
            if len(hsp_names) == 0:
                hsp_names = list(string.ascii_lowercase)[:len(hsp_index)]
                hsp_dict = {hsp_names[i]: [hsp_index[i]] for i in range(len(hsp_index))}
            
            elif len(hsp_names) == len(hsp_index):
                hsp_dict = {hsp_names[i]:[hsp_index[i]] for i in range(len(hsp_index))}
            
            elif  len(hsp_names) != len(hsp_index):
                print('hsp_names length in eigh function not match the separation detected in vasprun file, I will use the alphabet')
                hsp_names = list(string.ascii_lowercase)[:len(hsp_index)]
                hsp_dict = {hsp_names[i]: [hsp_index[i]] for i in range(len(hsp_index))}

            pd.DataFrame(hsp_dict).to_csv(self.path+'HSPinfo.csv',index=False)
            
            divisions = int(pathinfo[0][0])  #separation between paths
            npaths    = len(pathinfo[1:]) #number of paths sections
            hsp_index = [i*divisions  for i in range(npaths)]
            
            
            print('Charging kpoint path edges ...')
            kpnames = [kk.attrib['comment']   for kk in self.raiz.findall("./calculation/eigenvalues/array/set/set[@comment='spin 1']/")]  #set / spin  / kpoint
            # kpindex = range(len(kpnames))

            print('Charging Fermi level ...')
            Efermi  = float(self.raiz.findall("./calculation/dos/i")[0].text)

            print('Charging eigenvalues ...')

            bandnames = [bb.attrib['comment']   for bb in self.raiz.findall("./calculation/projected/array/set/set[@comment='spin1']/set[@comment='kpoint 1']/set")]
            bandindex = range(len(bandnames))    # bandnames  = ['band_{}'.format(kk) for kk in kpindex]

        
            spins = [ss.attrib['comment'] for ss in self.raiz.findall("./calculation/eigenvalues/array/set/set")]

            kinfo = pd.read_csv(self.path+'HSPinfo.csv').to_dict(orient='list')

            if 'spin 2' in spins:
                print('Spin polarized band calculation detected...')
                df_bands1 = pd.DataFrame(columns=bandnames, index=kpnames)  #SPIN up
                df_bands2 = pd.DataFrame(columns=bandnames, index=kpnames)  #SPIN down  
                for kk in kpnames:
                    
                    kkbb1 = (np.array([ np.array(eigen.text.split(),dtype=float)[0]  for eigen in self.raiz.findall("./calculation/eigenvalues/array/set/set[@comment='spin 1']/set[@comment='{}']/".format(kk))]) for bb in bandindex)
                    for bb1 in kkbb1:
                        df_bands1.loc[kk] = bb1-Efermi

                for kk in kpnames:

                    kkbb2 = (np.array([ np.array(eigen.text.split(),dtype=float)[0]  for eigen in self.raiz.findall("./calculation/eigenvalues/array/set/set[@comment='spin 2']/set[@comment='{}']/".format(kk))]) for bb in bandindex)
                    for bb2 in kkbb2:
                        df_bands2.loc[kk] = bb2-Efermi

                df_bands1.index.name = 'KP'
                df_bands2.index.name = 'KP'
                df = df_bands1.merge(df_bands2, left_on='KP', right_on='KP',suffixes=('_up','_down'))
                df.to_csv(self.path + 'bands.tar',compression={'method':'tar','archive_name':self.path + 'bands.csv'},chunksize=500)
                return1 =(df,hsp_dict) 

                return return1
            else:
                print('Non polarized band calculation detected...')
                
                df = pd.DataFrame(columns=bandnames, index=kpnames)  

                df.index.name = 'KP'

                for kk in kpnames:
                    kkbb1 = (np.array([ np.array(eigen.text.split(),dtype=float)[0]  for eigen in self.raiz.findall("./calculation/eigenvalues/array/set/set[@comment='spin 1']/set[@comment='{}']/".format(kk))]) for bb in bandindex)
                    for bb1 in kkbb1:
                        df.loc[kk] = bb1-Efermi

                df.to_csv(self.path+'bands.tar',    compression={'method':'tar','archive_name':self.path + 'bands.csv'},    chunksize=500)

                plotter(df,self.path,ylim=ylim,kinfo=kinfo,title=title, marker=marker,dpi=dpi,band_index=band_index,xhsp=xhsp,xshift=xshift)

                return1 = (df,hsp_dict)

                return return1
        else:
            print('bands.csv file detected, the data will be charged from this file')
            # print(self.route)
            df = pd.read_csv(self.route)
            if band_index == 'all':
                pass
            else:
                band_names= list(df.columns)[1:int(band_index)+1]
            # print(band_names,len(band_names))


            kinfo = pd.read_csv(self.path+'HSPinfo.csv').to_dict(orient='list')

            # kinfo.keys(hsp_names)
            kinfo = {hsp_names[n]: v for n, (k,v) in enumerate(kinfo.items()) }

            if plot==True:
                plotter(df,self.path,ylim=ylim,kinfo=kinfo,title=title, marker=marker,dpi=dpi,band_index=band_index,xhsp=xhsp,xshift=xshift)            
            else:
                pass
                
            return df
