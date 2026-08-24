import data_loader, analise, estatistica, modelos, argparse, json, getdist, matplotlib
import numpy as np
from pathlib import Path
from getdist import plots
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use('Agg')
plt.rcParams['text.usetex'] = True

def get_parametros(modelo, pack_dados):
    indices = modelos.MODELOS[modelo]['index']
    n_par = len(indices)

    def lnlike(**kwargs):
        theta = np.zeros(n_par)

        for par, ind in indices.items():
            theta[ind] = kwargs[par]
        
        return estatistica.lnprob(theta, modelo, pack_dados)
    
    return lnlike

def get_run_tag(nlive, seed):
    return f"nlive{nlive}_seed{seed}"

def get_chain_path(modelo, nome_dados, nlive, seed):
    run_tag = get_run_tag(nlive, seed)
    nome_modelo = modelos.MODELOS[modelo]['modelo']
    return Path('chains') / nome_modelo / nome_dados / run_tag / f'{nome_modelo}_{nome_dados}'

def build_info_dict(modelo, pack_dados, nlive, seed):
    parametros = list(modelos.MODELOS[modelo]['params'].keys())

    path = get_chain_path(modelo, pack_dados['data'], nlive, seed)

    info = {
        'likelihood': {
            'lnlike': {
                'external': get_parametros(modelo, pack_dados),
                'input_params': parametros
            }
        },

        'params': modelos.MODELOS[modelo]['params'],

        'sampler': {
            'polychord': {
                'nlive': nlive,
                'seed': seed
            }
        },

        'output': str(path)
    }

    info_post = {
        'output': str(path),
        'post': {
            'skip_samples': 0.3,
            'suffix': '_post'
        }
    }

    return info, info_post

def salvar_resultados(gdsamples, args, dados, nlive, tempo=False):
    print('\n'+30*'=')
    print('PROCESSANDO RESULTADOS')
    print(30*'='+'\n')

    resultados = analise.MCResult(gdsamples)

    path_chain = get_chain_path(args.modelo, dados['data'], nlive, args.seed)
    path_logz = Path(str(path_chain) + '.logZ')

    with open(path_logz, 'r') as file:
        for line in file:
            if 'logZ:' in line:
                logz = float(line.replace('logZ: ', '').strip())
            elif 'logZstd:' in line:
                logz_err = float(line.replace('logZstd: ', '').strip())
        
    n_dados = 0.0

    if 'CC' in dados:
        n_dados += len(dados['CC']['z'])
    if 'SNe' in dados:
        n_dados += len(dados['SNe']['z'])
    if 'BAO_SeB' in dados:
        n_dados += len(dados['BAO_SeB']['z'])
    if 'BAO_DESI' in dados:
        n_dados += len(dados['BAO_DESI']['z'])
    
    n_params = len(modelos.MODELOS[args.modelo]['index'])
    BIC, chi2min = estatistica.deltaBIC(gdsamples, n_dados, n_params)
    chi2red = chi2min/(n_dados-n_params)

    resultados.update({
        'logZ': {
            'media': logz,
            'err': logz_err
        },
        'chi2': {
            'chi2min': chi2min,
            'chi2red': chi2red,
            'n_dados': n_dados,
            'n_params': n_params,
            'BIC': BIC
        },
        'nlives': nlive,
        'sampler_seed': args.seed,
        'mock_generator': args.mock,
        'tempo': tempo})

    run_tag = get_run_tag(nlive, args.seed)
    pasta_path = Path(__file__).resolve().parent.parent.parent / 'resultados' / args.modelo / dados['data'] / run_tag
    print(f"\nCriando diretório {pasta_path}...\n")
    pasta_path.mkdir(parents=True, exist_ok=True)

    nome_arq = f"resultado_{args.modelo}_{dados['data']}.json"
    path_arq = pasta_path / nome_arq

    print(f'\nSalvando resultados em {path_arq}...\n')

    class NumpyEncoder(json.JSONEncoder):
        def dedfault(self, obj):
            if isinstance(obj, np.integer): return int(obj)
            if isinstance(obj, np.floating): return float(obj)
            if isinstance(obj, np.ndarray): return obj.tolist()
            return super(NumpyEncoder, self).default(obj)
    
    with open(path_arq, 'w') as file:
        json.dump(resultados, file, indent=4, cls=NumpyEncoder)

    indices = modelos.MODELOS[args.modelo]['index']
    lista_ordenada = sorted(indices, key=indices.get)
    params_plot = lista_ordenada[1:]
    legenda = f"{args.modelo} com {dados['data']}".replace('&', '\\&')

    print(f'\nGerando plot para {params_plot}...\n')

    g = plots.getSubplotPlotter()
    g.triangle_plot([gdsamples], params_plot, filled=False, legend_labels=[legenda])

    path_pdf = pasta_path / f"contornos_{args.modelo}_{dados['data']}.pdf"
    g.export(str(path_pdf))
    plt.close()
    print('\n\n ARQUIVOS SALVOS COM SUCESSO! \n\n')

parser = argparse.ArgumentParser(description='Expansão da distância comóvel por aproximantes de Padé.')
lista_modelos = list(modelos.MODELOS.keys())

parser.add_argument('--modelo', type=str, required=True, choices=lista_modelos)
parser.add_argument('--nlive', type=int, required=True)
parser.add_argument('--dados', nargs='+', required=True)
parser.add_argument('--sh0es', action='store_true')
parser.add_argument('--run', action='store_true')
parser.add_argument('--process', action='store_true')
parser.add_argument('--bestfit', action='store_true')
parser.add_argument('--zmax', type=float, default=None, help='Redshift máximo usado nos dados de BAO')
parser.add_argument('--seed', type=int, default=42, help='Seed do PyPolyChord')
parser.add_argument('--mock', type=str, default='False', help='Para usar dados sintéticos')

args = parser.parse_args()

if __name__ == '__main__':
    if args.run or args.bestfit:
        base_dir = Path(__file__).resolve().parent.parent.parent
        match args.mock:
            case 'False':
                data_path = base_dir/'dados'
                mock_prefix = ''
            case 'LCDM':
                data_path = base_dir/'mock_data'/'LCDM'
                mock_prefix = 'mock_LCDM_'
            case 'P21':
                data_path = base_dir/'mock_data'/'P21'
                mock_prefix = 'mock_P21_'
            case 'P22':
                data_path = base_dir/'mock_data'/'P22'
                mock_prefix = 'mock_P22_'
            case 'P31':
                data_path = base_dir/'mock_data'/'P31'
                mock_prefix = 'mock_P31_'
            case _:
                parser.error('--mock deve ser "False", "LCDM", "P21", "P22" ou "P31".')
        dados = {}
        if any(dado.lower() == 'cc' for dado in args.dados):
            print('\nCarregando dados de cronômetros cósmicos...')
            path_dados = data_path/'33CCdata.dat'
            path_cov = base_dir/'dados'/'data_MM20.dat'
            dados_cc = data_loader.load_cronometros(str(path_dados), str(path_cov), mock=(args.mock != 'False'), zmax=args.zmax)
            if not dados:
                dados.update({'data': f'{mock_prefix}CC', 'CC': dados_cc})
            else:
                dados.update({'data': f'{dados["data"]}+CC', 'CC': dados_cc})

        if any(dado.lower() == 'sne' for dado in args.dados):
            print(f'\nCarregando dados de supernovas (SH0ES={args.sh0es})...')
            path_dados = data_path/'Pantheon+SH0ES.dat'
            path_cov = base_dir/'dados'/'Pantheon+SH0ES_STAT+SYS.cov'
            dados_sne = data_loader.load_supernovas(str(path_dados), str(path_cov), sh0es=args.sh0es, zmax=args.zmax)
            if args.sh0es:
                nome = 'Pantheon+&SH0ES'
            else:
                nome = 'Pantheon+'
            if not dados:
                dados.update({'data': f'{mock_prefix}'+nome, 'SNe': dados_sne})
            else:
                dados.update({'data': f'{dados["data"]}+{nome}', 'SNe': dados_sne})

        if any(dado.lower() == 'bao_seb' for dado in args.dados):
            print(f'\nCarregando dados de BAO de Staicova & Benisty 2022...')
            path_dados = data_path/'DA_rd18.txt'
            dados_bao = data_loader.load_BAO_SeB(str(path_dados), zmax=args.zmax)
            if not dados:
                dados.update({'data': f'{mock_prefix}BAO_SeB', 'BAO_SeB': dados_bao})
            else:
                dados.update({'data': f'{dados["data"]}+BAO_SeB', 'BAO_SeB': dados_bao})
        
        if any(dado.lower() == 'bao_desi' for dado in args.dados):
            print(f'\nCarregando dados de BAO do DESI DR2...')
            path_dados = data_path/'desi_gaussian_bao_ALL_GCcomb_mean.txt'
            path_cov = base_dir/'dados'/'desi_gaussian_bao_ALL_GCcomb_cov.txt'
            dados_bao = data_loader.load_BAO_DESI(str(path_dados), str(path_cov), zmax=args.zmax)

            if not dados:
                dados.update({'data': f'{mock_prefix}BAO_DESI', 'BAO_DESI': dados_bao})
            else:
                dados.update({'data': f'{dados["data"]}+BAO_DESI', 'BAO_DESI': dados_bao})

        if args.zmax is not None:
            dados.update({'data': f'{dados["data"]}_zmax{args.zmax:g}'})
        
        print(args.dados)
        
        print('-'*30)
        print(f'SIMULAÇÃO PARA O MODELO {args.modelo}')
        print('-'*30+'\n')

        info, info_post = build_info_dict(args.modelo, dados, args.nlive, args.seed)

        print('-'*30)
        print(f'Iniciando PyPolyChord com {args.nlive} live points...')
        print('-'*30+'\n')

        sampler, sampler_post, tempo = analise.run_cobaya(info, info_post)

        if hasattr(sampler_post, 'products'):
            gdsamples = sampler_post.products()['sample'][0].to_getdist()
        else:
            gdsamples = sampler_post

        salvar_resultados(gdsamples, args, dados, args.nlive, tempo)

        print('\n'+30*'-')
        print('SIMULAÇÃO ENCERRADA')
        print('-'*30+'\n')

    if args.bestfit:
        par_ml = list(modelos.MODELOS[args.modelo]['values'].values())
        par_names = list(modelos.MODELOS[args.modelo]['values'].keys())

        print("\n")
        print("-"*30)
        print("CALCULANDO BESTFIT")
        print("-"*30)
        print("\n")

        run_tag = get_run_tag(args.nlive, args.seed)
        pasta_path = Path(__file__).resolve().parent.parent / 'resultados' / args.modelo / dados['data'] / run_tag
        print(f"\nCriando diretório {pasta_path}...\n")
        pasta_path.mkdir(parents=True, exist_ok=True)

        nome_arq = f"bestfit_{args.modelo}_{dados['data']}.txt"
        path_arq = pasta_path / nome_arq
        
        result, tempo = analise.find_bestfit(estatistica.lnprob, par_names, par_ml, args.modelo, dados)
    
        with open(path_arq, 'w') as arquivo:
            arquivo.write("--- Resultado do bestfit ---\n\n")
            
            arquivo.write(f"Sucesso: {result['success']}\n")
            arquivo.write(f"Mensagem: {result['message']}\n")
            arquivo.write(f"Chi2 mínimo: {result['fun']:.5f}\n")
            arquivo.write(f"Número de iterações: {result['nit']}\n")
            arquivo.write(f"Tempo total de execução: {tempo} segundos\n\n")
            
            arquivo.write("Valores dos parâmetros para likelihood máxima:\n")
            for i in range(len(par_names)):
                arquivo.write(f"{par_names[i]}: {result['x'][i]:.10f}\n")
                
        print(f"Bestfit salvos em {path_arq}\n")
