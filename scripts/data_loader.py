import numpy as np
import pandas as pd

# Carregar dados de Cronômetros Cósmicos
def load_cronometros(arquivo_dados, arquivo_cov):
    z, Hz, errHz = np.genfromtxt(arquivo_dados, comments='#', usecols=(0,1,2), unpack=True)
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
    inv_cov = np.linalg.inv(cov_mat)

    return {
        'z': z,
        'Hz': Hz,
        'inv_cov': inv_cov
    }

# Carregar dados de Supernovas
def load_supernovas(arquivo_dados, arquivo_cov, sh0es=True):
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

    inv_cov = np.linalg.inv(cov_mat)

    if sh0es:
        is_calibrator = dados['IS_CALIBRATOR'][ww]
        cepheid_distance = dados['CEPH_DIST'][ww]

        return {
            'z': zCMB,
            'zHEL': zHEL,
            'm_obs': m_obs,
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
            'inv_cov': inv_cov,
            'SH0ES': sh0es
            }

# Carregar dados de BAO Staicova & Benisty 2022
def load_BAO_SeB(arquivo_dados):
    zBAO, dA_rd, sdArd = np.genfromtxt(arquivo_dados, unpack=True)
    inv_cov = np.diag(1.0/sdArd**2)

    return {
        'z': zBAO,
        'dA_rd': dA_rd,
        'inv_cov': inv_cov
    }

# Carregar dados de BAO do DESI DR2
def load_BAO_DESI(arquivo_dados, arquivo_cov):
    dt = np.dtype([('z', 'f8'), ('value', 'f8'), ('quantity', 'U15')])
    zBAO, meanBAO, BAOtype = np.genfromtxt(arquivo_dados, dtype=dt, comments='#', unpack=True)
    cov_mat = np.genfromtxt(arquivo_cov)
    inv_cov = np.linalg.inv(cov_mat)

    return {
        'z': zBAO,
        'mean': meanBAO,
        'type': BAOtype,
        'inv_cov': inv_cov
    }