from getdist import loadMCSamples, plots
import matplotlib.pyplot as plt

def gerar_plot(nome, samples, params, labels, filled=False, fonte_legenda=16):
    g = plots.getSubplotPlotter()
    g.settings.legend_fontsize = fonte_legenda
    g.settings.axes_fontsize = 14
    g.settings.axes_labelsize = 16
    g.triangle_plot(samples, params, filled=filled, legend_labels=labels, legend_loc='upper right')
    g.export('./plots/P21/'+nome+'.pdf')

path_cc = './scripts/chains/P21/CC/P21_CC'
path_ps='./scripts/chains/P21/Pantheon+&SH0ES/P21_Pantheon+&SH0ES'
path_bao='./scripts/chains/P21/BAO_SeB/P21_BAO_SeB'

sample_cc=loadMCSamples(path_cc)
sample_ps=loadMCSamples(path_ps)
sample_bao=loadMCSamples(path_bao)

param_h0_bao = sample_bao.getParamNames().parWithName('h0')
if param_h0_bao is not None:
    param_h0_bao.name = 'h0_ignorado'
    # Atualiza as referências e os mapeamentos internos do objeto GetDist
    sample_bao.setParamNames(sample_bao.getParamNames())

params = ['h0', 'q0', 'j0']

samples = [sample_cc, sample_ps, sample_bao]

samples_labels = ['CC', 'Pantheon+&SH0ES','BAO']

gerar_plot('comp_cc_sn_baonoh0', samples, params, samples_labels, fonte_legenda=24)