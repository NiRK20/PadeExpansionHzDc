from getdist import loadMCSamples, plots
import matplotlib.pyplot as plt

def gerar_plot(nome, samples, params, labels, filled=False, fonte_legenda=16):
    g = plots.getSubplotPlotter()
    g.settings.legend_fontsize = fonte_legenda
    g.settings.axes_fontsize = 14
    g.settings.axes_labelsize = 16
    g.triangle_plot(samples, params, filled=filled, legend_labels=labels, legend_loc='upper right')
    g.export('./plots/CC+PS+BAO/'+nome+'.pdf')

path_P21='./scripts/chains/P21/PS/PS_P21'
path_P22='./scripts/chains/P22/PS/PS_P22'
path_P31='./scripts/chains/P31/PS/PS_P31'
path_P32='./scripts/chains/P32/PS/PS_P32'

sample_P21=loadMCSamples(path_P21)
sample_P22=loadMCSamples(path_P22)
sample_P31=loadMCSamples(path_P31)
sample_P32=loadMCSamples(path_P32)

params = ['h0', 'q0', 'j0', 's0', 'l0']
params_l0 = ['h0', 'q0', 'j0', 's0']
params_s0 = ['h0', 'q0', 'j0']

samples = [sample_P21, sample_P22, sample_P31, sample_P32]
samples_P32 = [sample_P21, sample_P22, sample_P31]

samples_labels = ['$P_{21}$', '$P_{22}$','$P_{31}$','$P_{32}$']
samples_P32_labels = ['$P_{21}$', '$P_{22}$','$P_{31}$']

nome = 'CC+Pantheon+&SH0ES+BAO_'

gerar_plot(nome+'all', samples, params, samples_labels, fonte_legenda=24)
gerar_plot(nome+'all_filled', samples, params, samples_labels, filled=True, fonte_legenda=24)

gerar_plot(nome+'all_l0', samples, params_l0, samples_labels, fonte_legenda=20)
gerar_plot(nome+'all_l0_filled', samples, params_l0, samples_labels, filled=True, fonte_legenda=20)

gerar_plot(nome+'all_s0', samples, params_s0, samples_labels, fonte_legenda=18)
gerar_plot(nome+'all_s0_filled', samples, params_s0, samples_labels, filled=True, fonte_legenda=18)

gerar_plot(nome+'no_P32', samples_P32, params_l0, samples_labels, fonte_legenda=20)
gerar_plot(nome+'no_P32_filled', samples_P32, params_l0, samples_labels, filled=True, fonte_legenda=20)

gerar_plot(nome+'no_P32_s0', samples_P32, params_s0, samples_labels, fonte_legenda=18)
gerar_plot(nome+'no_P32_s0_filled', samples_P32, params_s0, samples_labels, filled=True, fonte_legenda=18)

gerar_plot(nome+'P21', sample_P21, params_s0, ['$P_{21}$'])
gerar_plot(nome+'P22', sample_P22, params_l0, ['$P_{22}$'])
gerar_plot(nome+'P31', sample_P31, params_l0, ['$P_{31}$'])
gerar_plot(nome+'P32', sample_P32, params, ['$P_{32}$'])
