import vsp_band_plotter.read_bands_xml  as rvasp
import matplotlib.pyplot as plt
import pandas as pd
path         = '/scratch/rguerrero/TLG/Multilayers/bilayergraphene_trigonalwarping/fromrelaxation/tiltingcell/5_degrees/bands'+'/'   #path where the python code is 
file1        = path+'vasprun.xml'  #path where the vasprun is

# rvasp.bands_df(file1).pinta()
band= rvasp.bands_df(file1).eigh(plot=True,band_index='all', 
                                hsp_names = ['G1','Y','X1','N','X','G2'], 
                                ylim=(-0.5,0.5),title='',marker=''
                                ,dpi=350,xhsp=[3,6])
# data = pd.read_csv(path+'bands.csv')
# print(data.columns)

