from getdist import loadMCSamples, plots
import matplotlib.pyplot as plt

plt.rcParams['text.usetex'] = True

ANALISES = {
    'analise_1': {
        'modelo': 'P21',
        'modelo_tex': '$P_{21}$',
        'dados': ['cc', 'sne', 'bao_desi', 'sh0es'],
        'nlive': 500,
        'seed': 42
    }
}


def montar_amostras(analise):
    modelo = analise['modelo']
    plot_label = analise['modelo_tex']
    dados = analise['dados']
    nlive = analise['nlive']
    seed = analise['seed']
    
    data_string_parts = []

    if 'cc' in dados:
        data_string_parts.append('CC')

    if 'sne' in dados:
        if 'sh0es' in dados:
            data_string_parts.append('Pantheon+&SH0ES')
        else:
            data_string_parts.append('Pantheon+')

    if 'bao_desi' in dados:
        data_string_parts.append('BAO_DESI')

    if 'bao_seb' in dados:
        data_string_parts.append('BAO_SeB')

    data_string = '+'.join(data_string_parts)

    nome_arquivo = f'{modelo}_{data_string}'
    path_arquivo = f'{modelo}/{data_string}/nlive{nlive}_seed{seed}/{nome_arquivo}'
    samples = loadMCSamples(f'./scripts/motor/chains/{path_arquivo}')

    save_path = f'./plots/{path_arquivo}'

    return samples, plot_label, save_path


def plotar_amostra(samples, params, label, save_path, ftype='pdf', fonte_legenda=16, param_limits=None, filled=False):
    g = plots.getSubplotPlotter(width_inch=7, scaling=False)
    g.settings.legend_fontsize = fonte_legenda
    g.settings.axes_fontsize = 14
    g.settings.axes_labelsize = 16
    g.triangle_plot(samples, params, filled=filled, legend_labels=label, legend_loc='upper right', param_limits=param_limits or {})
    g.export(f'{save_path}.{ftype}')


samples = []
labels = []

for analise in list(ANALISES.keys()):
    sample, label, _ = montar_amostras(ANALISES[analise])
    samples.append(sample)
    labels.append(label)

params = ['h0', 'q0', 'j0']
#limites = {'s0': [-10.0, 25.0]}
#           'j0': [-0.5, 1.0]}

save_path = f'./plots/P21/CC+Pantheon+&SH0ES+BAO_DESI/nlive500_seed42/P21_CC+Pantheon+&SH0ES+BAO_DESI'


plotar_amostra(samples, params, labels, save_path)#, param_limits=limites)
print('Plot feito com sucesso!')








    
'''
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
            nome_arquivo = f'{modelo}_{string}'

    samples = []
    for path in paths:
        samples.append(loadMCSamples(path))

    return samples, labels, nome_arquivo
'''