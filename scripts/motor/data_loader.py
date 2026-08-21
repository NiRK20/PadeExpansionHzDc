import numpy as np
import pandas as pd
from pathlib import Path

# Carregar dados de Cronômetros Cósmicos
def load_cronometros(arquivo_dados, arquivo_cov, mock, zmax=None):
    if mock:
        zfile, Hzfile = np.genfromtxt(arquivo_dados, comments='#', usecols=(0,1), unpack=True)
        z, Hz, errHz = np.genfromtxt(Path(__file__).resolve().parent.parent.parent / 'dados' / '33CCdata.dat', comments='#', usecols=(0,1, 2), unpack=True)
    else:
        z, Hz, errHz = np.genfromtxt(arquivo_dados, comments='#', usecols=(0,1, 2), unpack=True)
        zfile = z
        Hzfile = Hz
    
    zmod, imf, spsooo = np.genfromtxt(arquivo_cov, comments='#', usecols=(0,1,4), unpack=True)

    n_dados = len(Hz)
    cov_diag = np.zeros((n_dados, n_dados), dtype='float64')

    # Erros estatísticos
    for i in range(n_dados):
        cov_diag[i][i] = errHz[i]**2
    
    # Erros sistemáticos
    imf_intp = np.interp(z, zmod, imf)/100
    sps_intp = np.interp(z, zmod, spsooo)/100

    cov_imf = np.zeros((n_dados, n_dados), dtype='float64')
    cov_sps = np.zeros((n_dados, n_dados), dtype='float64')

    for i in range(n_dados):
        for j in range(n_dados):
            cov_imf[i,j] = Hz[i] * imf_intp[i] * Hz[j] * imf_intp[j]
            cov_sps[i,j] = Hz[i] * sps_intp[i] * Hz[j] * sps_intp[j]
    
    # Matriz de covariância completa
    cov_mat = cov_diag + cov_imf + cov_sps

    if zmax is not None:
        mascara = zfile <= zmax

        zfile = zfile[mascara]
        Hzfile = Hzfile[mascara]
        cov_mat = cov_mat[np.ix_(mascara, mascara)]
    
    inv_cov = np.linalg.inv(cov_mat)

    return {
        'z': zfile,
        'Hz': Hzfile,
        'cov_mat': cov_mat,
        'inv_cov': inv_cov
    }

# Carregar dados de Supernovas
def load_supernovas(arquivo_dados, arquivo_cov, sh0es=True, zmax=None):
    dados = pd.read_csv(arquivo_dados, sep=r'\s+')
    n_dados_orig = len(dados)

    if sh0es:
        ww = (dados['zHD'] > 0.01) | (np.array(dados['IS_CALIBRATOR'], dtype=bool))
        zHEL = dados['zHEL'][ww]
    else:
        ww = (dados['zHD'] > 0.01)
        zHEL = dados['zHEL'][ww]
    
    zCMB = dados['zHD'][ww]
    m_obs = dados['m_b_corr'][ww]

    arq_cov = open(arquivo_cov)
    _ = arq_cov.readline()

    n_dados = len(zCMB)

    cov_mat = np.zeros((n_dados, n_dados))
    ii = -1
    
    for i in range(n_dados_orig):
        jj = -1
        if ww[i]:
            ii += 1
        for j in range(n_dados_orig):
            if ww[j]:
                jj += 1
            valor = float(arq_cov.readline())
            if ww[i]:
                if ww[j]:
                    cov_mat[ii, jj] = valor
    
    arq_cov.close()

    if zmax is not None:
        mascara = zCMB <= zmax

        zCMB = zCMB[mascara]
        zHEL = zHEL[mascara]
        m_obs = m_obs[mascara]
        cov_mat = cov_mat[np.ix_(mascara, mascara)]

    inv_cov = np.linalg.inv(cov_mat)

    if sh0es:
        is_calibrator = dados['IS_CALIBRATOR'][ww]
        cepheid_distance = dados['CEPH_DIST'][ww]
        if zmax is not None:
            is_calibrator = is_calibrator[mascara]
            cepheid_distance = cepheid_distance[mascara]

        return {
            'z': zCMB,
            'zHEL': zHEL,
            'm_obs': m_obs,
            'cov_mat': cov_mat,
            'inv_cov': inv_cov,
            'SH0ES': sh0es,
            'is_calibrator': is_calibrator,
            'cepheid_distance': cepheid_distance
            }
    else:
        return {
            'z': zCMB,
            'zHEL': zHEL,
            'm_obs': m_obs,
            'cov_mat': cov_mat,
            'inv_cov': inv_cov,
            'SH0ES': sh0es
            }

# Carregar dados de BAO Staicova & Benisty 2022
def load_BAO_SeB(arquivo_dados, zmax=None):
    zBAO, dA_rd, sdArd = np.genfromtxt(arquivo_dados, unpack=True)
    cov_mat = np.diag(sdArd**2)

    if zmax is not None:
        mascara = zBAO <= zmax

        zBAO = zBAO[mascara]
        dA_rd = dA_rd[mascara]
        cov_mat = cov_mat[np.ix_(mascara, mascara)]
    
    inv_cov = np.linalg.inv(cov_mat)

    return {
        'z': zBAO,
        'dA_rd': dA_rd,        
        'cov_mat': cov_mat,
        'inv_cov': inv_cov
    }

# Carregar dados de BAO do DESI DR2
def load_BAO_DESI(arquivo_dados, arquivo_cov, zmax=None):
    dt = np.dtype([('z', 'f8'), ('value', 'f8'), ('quantity', 'U15')])
    zBAO, meanBAO, BAOtype = np.genfromtxt(arquivo_dados, dtype=dt, comments='#', unpack=True)
    cov_mat = np.genfromtxt(arquivo_cov)

    if zmax is not None:
        mascara = zBAO <= zmax

        zBAO = zBAO[mascara]
        meanBAO = meanBAO[mascara]
        BAOtype = BAOtype[mascara]

        cov_mat = cov_mat[np.ix_(mascara, mascara)]
    
    inv_cov = np.linalg.inv(cov_mat)

    return {
        'z': zBAO,
        'mean': meanBAO,
        'type': BAOtype,
        'cov_mat': cov_mat,
        'inv_cov': inv_cov
    }