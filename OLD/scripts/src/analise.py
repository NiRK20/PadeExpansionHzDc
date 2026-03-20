import time
import scipy.optimize as op
from getdist import MCSamples
import matplotlib.pyplot as plt
from cobaya import run

def find_bestfit(lnlike, parnames, par_ml, modelo, data):#,data):
    t1 = time.time()
    ndim = len(par_ml)
    chi2 = lambda *args: -2 * lnlike(*args)
    result = op.minimize(chi2, par_ml, args=(modelo, data))
    if not result['success']:
        result = op.minimize(chi2, par_ml, args=(modelo,data), method='Nelder-Mead',options={'maxiter': 10000})
    par_ml = result["x"]
    print('\n\nMaximum likelihood result:')
    for i in range(ndim):
        print(parnames[i],' = ',par_ml[i])
    print('chi2min =',result['fun'])
    t2 = time.time()
    print("tempo total: {0:5.3f} seg\n\n".format(t2-t1))
    return result, t2-t1

def run_cobaya(info, info_post):
    print("----- INICIANDO SAMPLER -----")
    t1 = time.time()

    # Roda o sampler
    updated_info, sampler = run(info)

    # Retira o início 
    print("----- RETIRANDO O INICIO -----")
    updated_info_post, sampler_post = run(info_post)

    t2 = time.time()-t1

    print(f"\n --- TEMPO DE EXECUÇÃO: {t2} segundos.")

    return sampler, sampler_post, t2

def MCResult_cobaya(sampler):
    if hasattr(sampler, "products"):
        gdsamples = sampler.products()["sample"][0].to_getdist()
    else:
        gdsamples = sampler
    stats = gdsamples.getMargeStats()

    resultados = {"params":{}}

    for par in stats.names[:gdsamples.samples.shape[1]-2]:
        par_stats = stats.parWithName(par.name)
        mean = par_stats.mean

        # Erros de 1-sigma (68% CL)
        lower_1s = par_stats.limits[0].lower
        upper_1s = par_stats.limits[0].upper

        # Erros de 2-sigma (95% CL)
        lower_2s = par_stats.limits[1].lower
        upper_2s = par_stats.limits[1].upper

        resultados["params"].update({par.name: {
            "mean": mean,
            "err_plus_1s": upper_1s - mean,
            "err_minus_1s": mean - lower_1s,
            "err_plus_2s": upper_2s - mean,
            "err_minus_2s": mean - lower_2s
        }})
            
    return resultados