import src.data_loader as dl
import src.modelos as mod
import src.analise as anl
import src.estatistica as est
import argparse
import numpy as np
import os
import json
from getdist import plots
import matplotlib.pyplot as plt
import matplotlib
from getdist import loadMCSamples
from pathlib import Path

matplotlib.use("Agg")

def get_parameters(modelo, data_pack):
    indices = mod.MODELOS[modelo]["index"]
    ndim = len(indices)

    def lnlike(**kwargs):
        theta = np.zeros(ndim)

        for par, ind in indices.items():
            theta[ind] = kwargs[par]

        return est.lnprob(theta, modelo, data_pack)

    return lnlike

def build_info_dict(modelo, data_pack, nlive):

    dict_params = mod.MODELOS[modelo]["params"]
    lista_params = list(dict_params.keys())

    path = f"chains/{mod.MODELOS[modelo]["model"]}/{data_pack["data"]}/{data_pack["data"]}_{mod.MODELOS[modelo]["model"]}"

    info = {
        "likelihood":{
            "lnlike": {
                "external": get_parameters(modelo, data_pack),
                "input_params": lista_params
            }
        },

        "params": mod.MODELOS[modelo]["params"],
    
        "sampler":{
            "polychord": {
                "nlive": nlive
            }
        },
    
        "output": path
    }

    info_post = {
        "output": path,
        "post": {
            "skip_samples": 0.3,
            "suffix": "_post"
        }
    }

    return info, info_post

def salvar_resultados(gdsamples, args, data, modelo_nome, tempo="Indisponível"):
    print("-"*30)
    print("PROCESSANDO OS RESULTADOS")
    print("-"*30)
    
    resultados = anl.MCResult_cobaya(gdsamples)
    
    path_chain_base = Path(f"chains/{args.modelo}/{data['data']}/{data['data']}_{args.modelo}")
    path_logz = path_chain_base.with_suffix(".logZ")
    
    logZ = 0.0
    try:
        if path_logz.exists():
            with open(path_logz, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    if "logZ" in line:
                        logZ = float(line.split(":")[1].strip())
                        break
        else:
            print(f"Aviso: Arquivo logZ não encontrado em {path_logz}")
    except Exception as e:
        print(f"Erro ao ler logZ: {e}")

    n_dados = len(data["CC"]["z"]) + len(data["SNe"]["z"])
    k_params = len(mod.MODELOS[args.modelo]["index"])
    BIC = est.deltaBIC(gdsamples, n_dados, k_params)

    resultados.update({"tempo": tempo, "logZ": logZ, "BIC": BIC})
    
    folder_path = Path("resultados") / args.modelo / data["data"]
    print(f"\nCriando diretório {folder_path}")
    folder_path.mkdir(parents=True, exist_ok=True)

    file_name = f"resultado_{args.modelo}_{data['data']}.json"
    path_json = folder_path / file_name

    print(f"\n\nSalvando dicionário de resultados em {path_json}\n\n")

    class NumpyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, np.integer): return int(obj)
            if isinstance(obj, np.floating): return float(obj)
            if isinstance(obj, np.ndarray): return obj.tolist()
            return super(NumpyEncoder, self).default(obj)

    with open(path_json, "w") as f:
        json.dump(resultados, f, indent=4, cls=NumpyEncoder)
    
    if data["data"] == "PP":
        legenda = "CC+Pantheon+"
    elif data["data"] == "PS":
        legenda = "CC+Pantheon+SH0ES"
    
    indices = mod.MODELOS[args.modelo]["index"]
    lista_ordenada = sorted(indices, key=indices.get) 
    params_plot = lista_ordenada[1:] # Remove o primeiro (M)

    print(f"\n\nGerando plot para: {params_plot}\n\n")
    
    g = plots.getSubplotPlotter()
    g.triangle_plot([gdsamples], params_plot, filled=False, legend_labels=[legenda], legend_loc='upper right')
    
    path_pdf = folder_path / f"contornos_{data['data']}_{args.modelo}.pdf"
    g.export(str(path_pdf))
    plt.close()
    print("\n\nArquivos salvos com sucesso.\n\n")

parser = argparse.ArgumentParser(description="Expansão da distância comóvel por aproximantes de Padé")

lista_modelos = list(mod.MODELOS.keys())

parser.add_argument(
    "--modelo",
    type = str,
    required = True,
    choices = lista_modelos
)

parser.add_argument(
    "--nlive",
    type = int,
    default = 250
)

parser.add_argument(
    "--sh0es",
    action = "store_true",
)

parser.add_argument(
    "--run",
    action = "store_true"
)

parser.add_argument(
    "--process",
    action = "store_true"
)

parser.add_argument(
    "--bestfit",
    action = "store_true"
)

args = parser.parse_args()

if __name__ == "__main__":
    if args.run or args.process or args.bestfit:    
        print(f"Carregando dados de cronômetros cósmicos")
        dados_cc = dl.load_chronometers("data/32CCdata.dat", "data/data_MM20.dat")
        print(f"Carregando dados de supernovas (SH0ES={args.sh0es})")
        dados_sne = dl.load_pantheon("data/Pantheon+SH0ES.dat", "data/Pantheon+SH0ES_STAT+SYS.cov", SH0ES=args.sh0es)
    
        if args.sh0es:
            data = {
                "data": "PS",
                "CC": dados_cc,
                "SNe": dados_sne
            }
        else:
            data = {
                "data": "PP",
                "CC": dados_cc,
                "SNe": dados_sne
            }
    if args.run:
        print("-"*30)
        print(f"SIMULAÇÃO PARA O MODELO {args.modelo}")
        print("-"*30)
        
        info, info_post = build_info_dict(args.modelo, data, args.nlive)
    
        print(f"\n\nIniciando PolyChord com {args.nlive} live points.\n\n")
        sampler, sampler_post, tempo = anl.run_cobaya(info, info_post)

        if hasattr(sampler_post, "products"):
            gdsamples = sampler_post.products()["sample"][0].to_getdist()
        else:
            gdsamples = sampler_post
    
        salvar_resultados(gdsamples, args, data, args.modelo, tempo)

        print("\n\nSimulação encerrada.\n\n")

    if args.process:        
        print(f"\n\nProcessando cadeias do modelo {args.modelo}\n\n")

        path_chain = f'chains/{args.modelo}/{data["data"]}/{data["data"]}_{args.modelo}'
        gdsamples = loadMCSamples(path_chain)
        
        salvar_resultados(gdsamples, args, data, args.modelo)

    if args.bestfit:
        par_ml = list(mod.MODELOS[args.modelo]["values"].values())
        par_names = list(mod.MODELOS[args.modelo]["values"].keys())

        print("\n")
        print("-"*30)
        print("Calculando bestfit")
        print("-"*30)
        print("\n")
        
        result, tempo = anl.find_bestfit(est.lnprob, par_names, par_ml, args.modelo, data)
        folder = Path("resultados") / args.modelo / data["data"]
        file = f"bestfit_{args.modelo}_{data["data"]}.txt"
        path = folder / file
        
        print(f"\nCriando diretório {folder}")
        folder.mkdir(parents=True, exist_ok=True)
    
        with open(path, 'w') as arquivo:
            arquivo.write("--- Resultado do bestfit ---\n\n")
            
            arquivo.write(f"Sucesso: {result['success']}\n")
            arquivo.write(f"Mensagem: {result['message']}\n")
            arquivo.write(f"Chi2 mínimo: {result['fun']:.5f}\n")
            arquivo.write(f"Número de iterações: {result['nit']}\n")
            arquivo.write(f"Tempo total de execução: {tempo} segundos\n\n")
            
            arquivo.write("Valores dos parâmetros para likelihood máxima:\n")
            for i in range(len(par_names)):
                arquivo.write(f"{par_names[i]}: {result['x'][i]:.10f}\n")
                
        print(f"Bestfit salvos em {path}\n")