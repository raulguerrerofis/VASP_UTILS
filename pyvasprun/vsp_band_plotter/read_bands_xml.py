import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import os
import string
# from pathlib import Path
# from matplotlib.collections import LineCollection

class bands_df:
    """Returns a pandas DataFrame with each band per column"""
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
            Switch on the plot in a png file.
        band_index :
            (Default value = 'all')
            Selection of the bands by their index.
        hsp_names : list
            (Default value = [])
            Setting of the high symmetry points manually.
        ylim : tuple
            (Default value = (None,None))
        title : str
            (Default value = '')
            Add a title to band structure plot.
        marker :
            (Default value = '')
            Set the marker.
        dpi :
            (Default value = 300)
            Set the dpi of the output file.
        xhsp :
            (Default value = [])
            Set the index of the high symmetry points, i.e., [0,3].
        xshift :
            (Default value = 50)
            If you are plotting around one certain high symmetry point, i.e., -(d+K)<-----K----->(d+K)
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
                df.to_csv(self.path + 'bands.csv',compression='tar',chunksize=500)
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

                df.to_csv(self.path+'bands.csv',compression='tar',chunksize=500)

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
                band_names= list(df.columns)[1:band_index+1]
            # print(band_names,len(band_names))


            kinfo = pd.read_csv(self.path+'HSPinfo.csv').to_dict(orient='list')

            # kinfo.keys(hsp_names)
            kinfo = {hsp_names[n]: v for n, (k,v) in enumerate(kinfo.items()) }

            if plot==True:
                plotter(df,self.path,ylim=ylim,kinfo=kinfo,title=title, marker=marker,dpi=dpi,band_index=band_index,xhsp=xhsp,xshift=xshift)            
            else:
                pass
                
            return df
def plotter(df, path, ylim=(None,None),kinfo=dict(),title='',marker='',dpi=300,band_index='all',xhsp=[],xshift=50):
    fig, ax  = plt.subplots()
    a,b      = ylim

    if'_up' in df.columns[1]:
        if band_index=='all':
            up   = [bb for bb in df.columns if '_up'in bb]
            down = [bb for bb in df.columns if '_down'in bb]
        else:
            band_index = band_index + 1
            up   = [bb for bb in df.columns if '_up'in bb][1:band_index]
            down = [bb for bb in df.columns if '_down'in bb][1:band_index]

        #Spin up plot - > red color
        df[up].plot(kind='line', ax=ax,  ls='-', lw=0.75, color='red',
                            legend=False,ylim=(a,b),   xlim=(df.index[0],df.index[-2]),
                            ylabel='energy (eV)',xlabel='',marker=marker)
        
        #Spin down plot - > blue color
        down = [bb for bb in df.columns if '_down'in bb]
        df[down].plot(kind='line', ax=ax,  ls='--', lw=0.75, color='blue',
                            legend=False,ylim=(a,b),   xlim=(df.index[0],df.index[-2]),
                            xlabel='',marker=marker)
    else:
        if band_index=='all':
            selbands = df.columns[1:]
        else :
            selbands = df.columns[1:band_index+1]
        
        df[selbands].plot(kind='line', ax=ax, legend=False, lw=0.65,c='blue',
                    xlim=(df.index[0],df.index[-2]),ylim = (a,b),
                    ylabel='energy (eV)', marker=marker, markersize=0.5)
        

    ax.axhline(0.0,c='gray',ls='-',lw=0.55,zorder=0)
    ax.set_xlabel('')

 
    kinfo_values= list(kinfo.values())
    kinfo_values[-1]=[kinfo_values[-1][0]-1]

    hsp_vals=[i[0]  for i in kinfo_values]


    if len(xhsp)==0:
        ax.set_xticks(hsp_vals)
        ax.set_xticklabels([r'$\Gamma$'if 'G' in i else  i for i in list(kinfo.keys())])
        [ax.axvline(v,c='gray',ls='-',lw=0.55,zorder=0 ) for v in hsp_vals]
        ax.set_xlim(xmin=np.min(hsp_vals),xmax=np.max(hsp_vals))
    else:
        hsp_vals  = hsp_vals[xhsp[0] : xhsp[1] ]
        ax.set_xticks(hsp_vals)

        hsp_names = [r'$\Gamma$'if 'G' in i else  i for i in list(kinfo.keys())[xhsp[0]:xhsp[1]]]
        print(hsp_names)
        [ax.axvline(v,   c='gray',   ls='-',     lw=0.55,    zorder=0 ) for v in hsp_vals]
        ax.set_xticklabels(hsp_names)
        ax.set_xlim(xmin=np.min(hsp_vals)+xshift,xmax=np.max(hsp_vals)-xshift)



   
    ax.set_title(title)
    plt.tight_layout()
    fig.savefig(path+'BANDS_vasp.png',format='png',dpi=dpi)