import numpy as np
import scipy.interpolate, modelos

zt = np.linspace(0, 2.5, 3000)

# Supernovas
def extract_theory_points(theory_x, theory_y, M, dados):
    zCMB = dados['z']
    zHEL = dados['zHEL']
    sh0es = dados['SH0ES']

    if sh0es:
        is_calibrator = dados['is_calibrator']
        cepheid_distance = dados['cepheid_distance']

        theory_ynew = zCMB*np.nan
        theory_ynew[np.array(is_calibrator, dtype='bool')] = cepheid_distance[np.array(is_calibrator, dtype='bool')]

        zcmb = zCMB[~np.array(is_calibrator, dtype='bool')]
        zhel = zHEL[~np.array(is_calibrator, dtype='bool')]
    else:
        theory_ynew = zCMB*np.nan

        zcmb = zCMB
        zhel = zHEL
    
    f = scipy.interpolate.interp1d(theory_x, theory_y)
    fz = f(zcmb)

    if np.any(fz <= 0):
        return None
    
    if sh0es:
        theory_ynew[~np.array(is_calibrator, dtype='bool')] = 5.0*np.log10((1.0+zcmb)*(1.0+zhel)*np.atleast_1d(fz)) + 25.0
    else:
        theory_ynew = 5.0*np.log10((1.0+zcmb)*(1.0+zhel)*np.atleast_1d(fz))+25.
    
    return theory_ynew + M

# Cronômetros cósmicos
def extract_theory_points_CC(theory_x, theory_y, dados):
    Hz = dados['z']
    theory_ynew = Hz*np.nan

    f = scipy.interpolate.interp1d(theory_x, theory_y)
    theory_ynew = np.atleast_1d(f(Hz))

    return theory_ynew

# region Chi^2
# Supernovas
def chi2_SNe(theta, modelo, dados):
    Ezt = modelos.MODELOS[modelo]['Ez'](dados['z'], theta)
    if np.any(Ezt <= 0):
        return np.inf

    dAt = modelos.dmModel(zt, theta, modelo)
    m_mod = extract_theory_points(zt, dAt, theta[0], dados)

    if m_mod is None:
        return np.inf
    
    m_obs = dados['m_obs']
    dm = m_mod - m_obs

    inv_cov = dados['inv_cov']

    if dados['SH0ES']:
        return np.dot(np.dot(dm.T, inv_cov), dm)
    else:
        Sa = np.sum(inv_cov)
        Sr = np.sum(np.dot(dm.t, inv_cov))
        Srr = np.dot(np.dot(dm.t, inv_cov), dm)
        return Srr - Sr**2.0/Sa

# Cronômetros cósmicos
def chi2_CC(theta, modelo, dados):
    Ezt = modelos.MODELOS[modelo]['Ez'](zt, theta)
    if np.any(Ezt <= 0):
        return np.inf
    
    Hzt = theta[1]*Ezt
    Hzm = extract_theory_points_CC(zt, Hzt, dados)

    Hz = dados['Hz']
    inv_cov = dados['inv_cov']
    dh = Hzm - Hz

    return np.dot(np.dot(dh.T, inv_cov), dh)

# BAO de Staicova & Benisty
def chi2_BAO_SeB(theta, modelo, dados):
    v_obs = dados['dA_rd']
    z_BAO = dados['z']
    inv_cov = dados['inv_cov']

    Ezt = modelos.MODELOS[modelo]['Ez'](z_BAO, theta)
    if np.any(Ezt <= 0):
        return np.inf
    
    f = modelos.MODELOS[modelo]['Dc'](z_BAO, theta)/(1 + z_BAO)
    A = np.dot(np.dot(f.T, inv_cov), f)
    B = 0.5*((np.dot(np.dot(f.T, inv_cov), v_obs)) + np.dot(np.dot(v_obs.T, inv_cov), f))
    C = np.dot(np.dot(v_obs.T, inv_cov), v_obs)
    return C - B**2/A + np.log(A/(2*np.pi))
# endregion

def lnprob(theta, modelo, pack_dados):
    chi2 = 0.0
    if 'CC' in pack_dados:
        chi2 += chi2_CC(theta, modelo, pack_dados['CC'])
    
    if 'SNe' in pack_dados:
        chi2 += chi2_SNe(theta, modelo, pack_dados['SNe'])

    if 'BAO_SeB' in pack_dados:
        chi2 += chi2_BAO_SeB(theta, modelo, pack_dados['BAO_SeB'])
    
    return -0.5 * chi2

def deltaBIC(samples, n, k):
    params = samples.getParams()

    if hasattr(params, 'chi2'):
        chi2min = np.min(params.chi2)
    elif hasattr(params, 'minuslogpost'):
        chi2min = 2 * np.min(params.minuslogpost)
    else:
        print('Aviso: chi2 não encontrada para essas amostras.')
        return 0
    
    BIC = chi2min + k*np.log(n)

    return BIC, chi2min