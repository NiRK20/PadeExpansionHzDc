import numpy as np
import pandas as pd

def load_chronometers(data_file, cov_file):
    zHz, Hzi, errHz = np.genfromtxt(data_file, comments='#', usecols=(0,1,2), unpack=True, delimiter=',')
    zmod, imf, slib, sps, spsooo = np.genfromtxt(cov_file, comments='#', usecols=(0,1,2,3,4), unpack=True)
    
    cov_mat_diag = np.zeros((len(zHz), len(zHz)), dtype='float64') 

    # Erros estatísticos
    for i in range(len(zHz)):
        cov_mat_diag[i,i] = errHz[i]**2
    
    # Erros sistemáticos
    imf_intp = np.interp(zHz, zmod, imf)/100
    spsooo_intp = np.interp(zHz, zmod, spsooo)/100
    
    cov_mat_imf = np.zeros((len(zHz), len(zHz)), dtype='float64')
    cov_mat_spsooo = np.zeros((len(zHz), len(zHz)), dtype='float64')
    
    for i in range(len(zHz)):
        for j in range(len(zHz)):
            cov_mat_imf[i,j] = Hzi[i] * imf_intp[i] * Hzi[j] * imf_intp[j]
            cov_mat_spsooo[i,j] = Hzi[i] * spsooo_intp[i] * Hzi[j] * spsooo_intp[j]
            
    # Matriz de covariância total
    cov_mat = cov_mat_spsooo+cov_mat_imf+cov_mat_diag
    inv_cov_mat = np.linalg.inv(cov_mat)

    return {
        "z": zHz,
        "Hz": Hzi,
        "inv_cov": inv_cov_mat
    }

def load_pantheon(data_file, cov_file, SH0ES=False):
    data = pd.read_csv(data_file, sep=r'\s+')
    origlen = len(data)
    
    if SH0ES:
        ww = (data['zHD']>0.01) | (np.array(data['IS_CALIBRATOR'],dtype=bool))
        zHEL = data['zHEL'][ww]
    else:
        ww = (data['zHD']>0.01)
        zHEL = data['zHEL'][ww]

    zCMB = data['zHD'][ww]
    m_obs = data['m_b_corr'][ww]
    
    f = open(cov_file)
    line = f.readline()
    
    n = int(len(zCMB))
    
    C = np.zeros((n,n))
    ii = -1
    jj = -1
    mine = 999
    maxe = -999
    for i in range(origlen):
        jj = -1
        if ww[i]:
            ii += 1
        for j in range(origlen):
            if ww[j]:
                jj += 1
            val = float(f.readline())
            if ww[i]:
                if ww[j]:
                    C[ii,jj] = val
    f.close()

    inv_cov = np.linalg.inv(C)
    
    if SH0ES:
        is_calibrator = data['IS_CALIBRATOR'][ww]
        cepheid_distance = data['CEPH_DIST'][ww]
    
        return {
            "z": zCMB,
            "zHEL": zHEL,
            "m_obs": m_obs,
            "inv_cov": inv_cov,
            "SH0ES": SH0ES,
            "is_calibrator": is_calibrator,
            "cepheid_distance": cepheid_distance
        }
    else:
        return {
            "z": zCMB,
            "zHEL": zHEL,
            "m_obs": m_obs,
            "inv_cov": inv_cov,
            "SH0ES": SH0ES
        }