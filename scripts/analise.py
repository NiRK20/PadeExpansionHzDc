import time,  cobaya
import scipy.optimize as op

def find_bestfit(lnlike, parnames, par_ml, modelo, dados, show=False):
    t1 = time.time()
    n_par = len(par_ml)
    chi2 = lambda *args: -2 * lnlike(*args)
    result = op.minimize(chi2, par_ml, args=(modelo, dados))

    if not result['sucess']:
        result = op.minimize(chi2, par_ml, args=(modelo, dados), method='Nelder-Mead', options={'maxiter': 10000})
    
    par_ml = result['x']
    tempo_total = time.time()-t1
    if show:
        print('Resultado da likelihood máxima:')
        for i in range(n_par):
            print(f'{parnames[i]} = {par_ml[i]}')
        print(f"chi2min = {result['fun']}")
        print(f'Tempo total: {tempo_total:5.3f} s')

    return result, tempo_total

def run_cobaya(info, info_post):
    print('----- INICIANDO SAMPLER -----')
    t1 = time.time()

    _, sampler = cobaya.run(info)

    print('----- RETIRANDO O INÍCIO -----')
    _, sampler_post = cobaya.run(info_post)

    t_total = time.time() - t1

    print(f'\nTEMPO DE EXECUÇÃO: {t_total} s.')

    return sampler, sampler_post, t_total

def MCResult(sampler):
    if hasattr(sampler, 'products'):
        gdsamples = sampler.products()['sample'][0].to_getdist()
    else:
        gdsamples = sampler
    
    stats = gdsamples.getMargeStats()

    resultados = {'params': {}}

    for parametro in stats.names[:gdsamples.samples.shape[1]-2]:
        par_stats = stats.parWithName(parametro.name)

        media = par_stats.mean

        # Erros de 1s
        inf_1s = par_stats.limits[0].lower
        sup_1s = par_stats.limits[0].upper

        # Erros de 2s
        inf_2s = par_stats.limits[1].lower
        sup_2s = par_stats.limits[1].upper
    
        resultados['params'].update({parametro.name: {
            'media': media,
            'inf_1s': media - inf_1s,
            'sup_1s': sup_1s - media,
            'inf_2s': media - inf_2s,
            'sup_2s': sup_2s - media,
        }})
    
    return resultados