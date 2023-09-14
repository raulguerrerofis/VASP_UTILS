from .read_bands_xml import bands_df
from matplotlib.collections import LineCollection
import matplotlib.pyplot as plt
#General dependences
import pandas as pd
import numpy as np

plt.rcParams.update({"text.usetex": False,
                    "font.family": "sans-serif",
                    "text.antialiased": True,
                    "axes.unicode_minus":False,
                    "font.size":   11,
                    })
def plotter(df, path, ylim=(None,None),kinfo=dict(),title='',marker='',dpi=300,band_index='all',xhsp=[],xshift=50):
    """

    Parameters
    ----------
    df :
        
    path :
        
    ylim :
        (Default value = (None)
    None) :
        
    kinfo :
        (Default value = dict())
    title :
        (Default value = '')
    marker :
        (Default value = '')
    dpi :
        (Default value = 300)
    band_index :
        (Default value = 'all')
    xhsp :
        (Default value = [])
    xshift :
        (Default value = 50)

    Returns
    -------

    
    """
    fig, ax  = plt.subplots()
    a,b      = ylim

    if'_up' in df.columns[1]:
        if band_index=='all':
            up   = [bb for bb in df.columns if '_up'in bb]
            down = [bb for bb in df.columns if '_down'in bb]
        else:
            band_index = int(band_index) + 1
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
            selbands = df.columns[1:int(band_index)+1]
        
        df[selbands].plot(kind='line', ax=ax, legend=False, lw=0.65,c='blue',
                    xlim=(df.index[0],df.index[-2]),ylim = (a,b),
                    ylabel='energy (eV)', marker=marker, markersize=0.5)
        

    ax.axhline(0.0,c='gray',ls='-',lw=0.55,zorder=0)
    ax.set_xlabel('')

 
    kinfo_values= list(kinfo.values())
    kinfo_values[-1]=[kinfo_values[-1][0]-1]

    hsp_vals=np.array([i[0]  for i in kinfo_values],dtype=float)


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