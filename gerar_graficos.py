from getdist import loadMCSamples, plots
import matplotlib.pyplot as plt

analises = {
    'P21': [['sne', 'bao_seb', 'sh0es'], ['cc', 'sne', 'bao_seb', 'sh0es']]
}
nome_arquivo = 'test_CC_SH0ES_P21_SEB'

def gerar_plot(nome, samples, params, labels, filled=False, fonte_legenda=16, ftype='pdf', param_limits=None):
    g = plots.getSubplotPlotter(width_inch=7, scaling=False)
    g.settings.legend_fontsize = fonte_legenda
    g.settings.axes_fontsize = 14
    g.settings.axes_labelsize = 16
    g.triangle_plot(samples, params, filled=filled, legend_labels=labels, legend_loc='upper right', param_limits=param_limits or {})
    g.export('./plots/P21/'+nome+'.'+ftype)

def mount_samples(analises):

    def data_string(data):
        parts = []
    
        if 'cc' in data:
            parts.append('CC')
    
        if 'sne' in data:
            if 'sh0es' in data:
                parts.append('Pantheon+&SH0ES')
            else:
                parts.append('Pantheon+')
    
        if 'bao_desi' in data:
            parts.append('BAO_DESI')
    
        if 'bao_seb' in data:
            parts.append('BAO_SeB')
    
        return '+'.join(parts)
        
    paths = []
    labels = []
    for modelo in analises:
        for dados in analises[modelo]:
            string = data_string(dados)
            labels.append(string)
            paths.append(f'./scripts/motor/chains/{modelo}/{string}/{modelo}_{string}')

    samples = []
    for path in paths:
        samples.append(loadMCSamples(path))

    return samples, labels

'''
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
'''

params = ['h0', 'q0', 'j0']

samples, labels = mount_samples(analises)
#limites = {'q0': [-1.0, 0.0],
#           'j0': [-0.5, 1.0]}

gerar_plot(nome_arquivo, samples, params, labels, fonte_legenda=14, ftype='png')#, param_limits=limites)
print('Plot feito com sucesso!')