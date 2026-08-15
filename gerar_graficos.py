from getdist import loadMCSamples, plots
import matplotlib.pyplot as plt

def gerar_plot(nome, samples, params, labels, filled=False, fonte_legenda=16, ftype='pdf', param_limits=None):
    g = plots.getSubplotPlotter()
    g.settings.legend_fontsize = fonte_legenda
    g.settings.axes_fontsize = 14
    g.settings.axes_labelsize = 16
    g.triangle_plot(samples, params, filled=filled, legend_labels=labels, legend_loc='upper right', param_limits=param_limits or {})
    g.export('./plots/P21/'+nome+'.'+ftype)

path_cc = './scripts/chains/P21/CC/P21_CC'
path_ps='./scripts/chains/P21/Pantheon+&SH0ES/P21_Pantheon+&SH0ES'
path_pp='./scripts/chains/P21/Pantheon+/P21_Pantheon+'
path_bao_seb='./scripts/chains/P21/BAO_SeB/P21_BAO_SeB'
path_bao_desi='./scripts/chains/P21/BAO_DESI/P21_BAO_DESI'

sample_cc=loadMCSamples(path_cc)
sample_ps=loadMCSamples(path_ps)
sample_pp=loadMCSamples(path_pp)
sample_bao_seb=loadMCSamples(path_bao_seb)
sample_bao_desi=loadMCSamples(path_bao_desi)

param_h0_bao_seb = sample_bao_seb.getParamNames().parWithName('h0')
if param_h0_bao_seb is not None:
    param_h0_bao_seb.name = 'h0_ignorado'
    # Atualiza as referências e os mapeamentos internos do objeto GetDist
    sample_bao_seb.setParamNames(sample_bao_seb.getParamNames())

param_h0_bao_desi = sample_bao_desi.getParamNames().parWithName('h0')
if param_h0_bao_desi is not None:
    param_h0_bao_desi.name = 'h0_ignorado'
    # Atualiza as referências e os mapeamentos internos do objeto GetDist
    sample_bao_desi.setParamNames(sample_bao_desi.getParamNames())

param_h0_pp = sample_pp.getParamNames().parWithName('h0')
if param_h0_pp is not None:
    param_h0_pp.name = 'h0_ignorado'
    # Atualiza as referências e os mapeamentos internos do objeto GetDist
    sample_pp.setParamNames(sample_pp.getParamNames())

params = ['h0', 'q0', 'j0']

samples = [sample_cc, sample_ps, sample_bao_seb, sample_bao_desi]

samples_labels = ['CC', 'Pantheon+&SH0ES','BAO S&B', 'BAO DESI']
limites = {'q0': [-1.0, 0.0],
           'j0': [-0.5, 1.0]}

gerar_plot('P21_total', samples, params, samples_labels, fonte_legenda=18, ftype='png', param_limits=limites)
print('Plot feito com sucesso!')