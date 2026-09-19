"""Publication figures from the bundled fixed-index training samples."""
import hashlib,json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.colors import Normalize, SymLogNorm
from build_data import ROOT,NAMES,CLASS_OF,CLASS_ORDER,CLASS_LABELS,EXCLUSIONS,dump,load,ordered_datasets
from paper_scope import HISTORICAL_COUNT, PDE_COUNT, PAPER_COUNT

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'pdf.fonttype':42,'ps.fonttype':42})
CAVITY_KEYS=('lid_driven_cavity_v2',)
FIELD_CMAP='viridis'
DETAIL_CLASS_GROUPS=(('elliptic',),('diffusion','convection'),('shocks','porous'),
                     ('reaction_diffusion',),('waves',))

def detail_groups(order):
    return [[d for d in order if CLASS_OF[d] in group] for group in DETAIL_CLASS_GROUPS]

def cavity_norm(values):
    # Common signed scale retains all stored values, including the extreme walls.
    bound=float(100*np.ceil(max(np.abs(values[d]).max() for d in CAVITY_KEYS)/100))
    return SymLogNorm(linthresh=1,linscale=1,vmin=-bound,vmax=bound,base=10,clip=False)

def save(fig,name):
    fig.savefig(ROOT/'figures'/f'{name}.pdf',bbox_inches='tight',pad_inches=.025)
    fig.savefig(ROOT/'figures'/f'{name}.png',dpi=200,bbox_inches='tight',pad_inches=.025)
    plt.close(fig)

def fields():
    manifest=load(ROOT/'data/gallery_manifest.json');out={}
    with np.load(ROOT/'data/gallery_samples.npz') as z:
        for r in manifest['datasets']:
            a=z[r['dataset']+'__y']
            assert hashlib.sha256(a.tobytes()).hexdigest()==r['y']['sample_sha256']
            out[r['dataset']]=a.reshape(r['native_grid'])
    extra=load(ROOT/'data/four_dataset_completion/gallery_manifest.json')
    with np.load(ROOT/'data/four_dataset_completion/gallery_samples.npz') as z:
        for r in extra['datasets']:
            a=z[r['dataset']+'__y']
            assert hashlib.sha256(a.tobytes()).hexdigest()==r['y']['sample_sha256']
            out[r['dataset']]=a.reshape(r['native_grid'])
    return manifest,out

def gallery(manifest,values):
    cavity_scale=cavity_norm(values)
    main_datasets=load(ROOT/'data/individual_model_summary.json')['means']
    order=ordered_datasets(main_datasets)
    assert len(order)==PDE_COUNT and set(order)<=set(values)
    order=order+['era5']
    extra=[]
    fig,axes=plt.subplots(4,6,figsize=(7.1,4.35))
    for ax in list(axes.flat)[len(order):]:ax.axis('off')
    for i,(d,ax) in enumerate(zip(order,axes.flat)):
        a=values[d];lo,hi=float(a.min()),float(a.max())
        if d in CAVITY_KEYS:
            ax.imshow(a,cmap=FIELD_CMAP,norm=cavity_scale,origin='lower',aspect='equal',interpolation='nearest')
        else:
            ax.imshow((a-lo)/max(hi-lo,1e-30),cmap=FIELD_CMAP,vmin=0,vmax=1,origin='lower',aspect='auto',interpolation='nearest')
        title=NAMES[d].replace('--','–').replace(' (generated)',' (gen.)').replace(' (corrected)',' (fixed)')
        ax.set_title(f'{i+1}. {title}',fontsize=5.9,pad=3,loc='left')
        kind='space and time' if d.startswith('heat') else ('climate grid' if d=='era5' else 'spatial grid')
        ax.set_xlabel(f'{CLASS_LABELS[CLASS_OF[d]]}\n{a.shape[0]} × {a.shape[1]}  ·  {kind}',fontsize=5.1,labelpad=2)
        ax.set_xticks([]);ax.set_yticks([])
        for s in ax.spines.values():s.set_linewidth(.4);s.set_color('.7')
    fig.subplots_adjust(left=.01,right=.99,bottom=.045,top=.97,wspace=.12,hspace=.72)
    save(fig,'dataset_gallery')
    # Larger panels retain numerical ranges and native-array coordinates.
    detail_order=detail_groups(order)
    for part in range(6):
        if part==5:
            fig,ax=plt.subplots(figsize=(7.1,3.4))
            a=values['era5']
            im=ax.imshow(a,cmap=FIELD_CMAP,origin='lower',aspect='auto',interpolation='nearest')
            ax.set_title('ERA5',loc='left',fontsize=10)
            ax.set_xlabel('Stored column index');ax.set_ylabel('Stored row index')
            fig.colorbar(im,ax=ax,fraction=.035,pad=.025)
            fig.tight_layout();save(fig,'dataset_detail_6')
            continue
        fig,axes=plt.subplots(2,3,figsize=(7.1,4.8))
        chunk=detail_order[part]
        for ax in list(axes.flat)[len(chunk):]:ax.axis('off')
        for d,ax in zip(chunk,axes.flat):
            a=values[d]
            if d in CAVITY_KEYS:
                im=ax.imshow(a,cmap=FIELD_CMAP,norm=cavity_scale,origin='lower',aspect='equal',interpolation='nearest')
            else:
                im=ax.imshow(a,cmap=FIELD_CMAP,origin='lower',aspect='auto',interpolation='nearest')
            ax.set_title(NAMES[d].replace('--','–')+'\n'+CLASS_LABELS[CLASS_OF[d]],fontsize=8,loc='left')
            ax.set_xlabel('Spatial index' if d.startswith('heat') else 'Stored column index',fontsize=7);ax.set_ylabel('Time index' if d.startswith('heat') else 'Stored row index',fontsize=7)
            ax.tick_params(labelsize=6)
            cb=fig.colorbar(im,ax=ax,fraction=.035,pad=.025);cb.ax.tick_params(labelsize=6)
            if d in CAVITY_KEYS:
                cb.set_ticks([-100,-10,-1,0,1,10,100]);cb.ax.minorticks_off()
                cb.set_label('Vorticity, signed log',fontsize=6)
            cb.ax.yaxis.get_offset_text().set_fontsize(6)
        note='Stored HF target values\n\nNative array orientation.\nNo coordinate conversion.\n\nRow 0 of each training table.\nColor scales differ by panel.'
        if any(d in CAVITY_KEYS for d in chunk):
            note='Cavity shows vorticity.\nSigned log scale.\nSquare geometry preserved.\nAll values retained.\n\nRe = 594.23, training row 0.\n\nOther panels: linear scales.'
        if len(chunk)<len(axes.flat):
            axes.flat[-1].text(.0,.8,note,va='top',fontsize=9,linespacing=1.5)
        fig.tight_layout(w_pad=1.2,h_pad=1.3);save(fig,f'dataset_detail_{part+1}')
    return order,extra

def main():
    from build_overview import overview as revised_overview
    manifest,values=fields();order,extra=gallery(manifest,values);revised_overview(values)
    dump(ROOT/'qa/gallery_checks.json',dict(passed=True,datasets=len(order),archived_datasets=len(values),main_datasets=len(order),order=order,appendix_only=extra,
        class_order=list(CLASS_ORDER),class_labels_displayed=True,
        detail_groups=detail_groups(order),
        selection=f'First HF training row for each of the {PAPER_COUNT} paper entries. All {len(values)} archived sample hashes remain verified.',sample_hashes_verified=len(values),extension_sample_hashes_verified=4,
        main_panel_normalization='Cavity: signed logarithmic scale, linear within [-1,1], no clipping. Other fields: individual linear ranges.',
        field_colormap=FIELD_CMAP,
        cavity_scale=dict(kind='symmetric logarithmic',linear_threshold=1,bound=cavity_norm(values).vmax,
                          data_unchanged=True,dataset=CAVITY_KEYS[0]),
        orientation='Native array rows/columns, origin lower; no geographic or physical-axis claims',
        main_colorbars=False,main_era5_annotation=False,detailed_figures=6))
    print(f'Built graphical abstract, {PAPER_COUNT}-dataset main gallery ({HISTORICAL_COUNT} matched + ERA5), and five appendix plates.')

if __name__=='__main__':main()
