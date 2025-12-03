import numpy as np
import src.modelos as modelos
import scipy.interpolate

zt = np.linspace(0,2.5, 3000)

def extract_theory_points(theory_x, theory_y, M, data_dict):
    zCMB = data_dict["z"]
    zHEL = data_dict["zHEL"]
    SH0ES = data_dict["SH0ES"]

    f = scipy.interpolate.interp1d(theory_x, theory_y)
    
    if SH0ES:
        is_calibrator = data_dict['is_calibrator']
        cepheid_distance = data_dict['cepheid_distance']
        
        theory_ynew = zCMB*np.nan
        theory_ynew[np.array(is_calibrator,dtype='bool')] = cepheid_distance[np.array(is_calibrator,dtype='bool')]
        
        zcmb = zCMB[~np.array(is_calibrator,dtype='bool')]
        zhel = zHEL[~np.array(is_calibrator,dtype='bool')]
    else:
        theory_ynew = zCMB*np.nan
        
        zcmb = zCMB
        zhel = zHEL
    
    fz = f(zcmb)
    if np.any(fz<=0):
        return None
    if SH0ES:
        theory_ynew[~np.array(is_calibrator,dtype='bool')] = 5.0*np.log10((1.0+zcmb)*(1.0+zhel)*np.atleast_1d(fz))+25.
    else:
        theory_ynew = 5.0*np.log10((1.0+zcmb)*(1.0+zhel)*np.atleast_1d(fz))+25.
    
    return theory_ynew + M

def extract_theory_pointsHz(theory_x, theory_y, data_dict):
    zHz = data_dict["z"]
    theory_ynew = zHz*np.nan

    f = scipy.interpolate.interp1d(theory_x, theory_y)
    theory_ynew = np.atleast_1d(f(zHz))
    
    return theory_ynew
    
# Chi2 para Pantheon+SH0ES
def chi2_SNe(theta, modelo, data_dict):
    Ez2i = modelos.MODELOS[modelo]["Ez"](data_dict["z"], theta)
    if np.any(Ez2i <= 0):
        return np.inf

    dAt = modelos.dmModel(zt, theta, modelo)
    mmod = extract_theory_points(zt, dAt, theta[0], data_dict)

    if mmod is None:
        return np.inf

    m_obs = data_dict["m_obs"]
    dm = mmod - m_obs

    inv_cov = data_dict["inv_cov"]

    if data_dict["SH0ES"]:
        return np.dot(np.dot(dm.T,inv_cov),dm)

    else:
        SA  = np.sum(inv_cov)
        Sr  = np.sum(np.dot(dm.T,inv_cov))
        Srr = np.dot(np.dot(dm.T,inv_cov),dm)
        return Srr - Sr**2./SA

# Chi2 para CC
def chi2_Hz(theta, modelo, data_dict):
    Ezt = modelos.MODELOS[modelo]["Ez"](zt, theta)
    if np.any(Ezt <= 0):
        return np.inf
        
    Hzt = theta[1]*Ezt
    Hzm = extract_theory_pointsHz(zt, Hzt, data_dict)

    Hzi = data_dict["Hz"]
    inv_cov = data_dict["inv_cov"]
    dh = Hzm-Hzi
    
    return np.dot(np.dot(dh.T,inv_cov),dh)

def lnprob(theta, modelo, data_pack):
    chi2_total = 0.0
    if "CC" in data_pack:
        chi2_cc = chi2_Hz(theta, modelo, data_pack["CC"])
        chi2_total += chi2_cc

    if "SNe" in data_pack:
        chi2_sne = chi2_SNe(theta, modelo, data_pack["SNe"])
        chi2_total += chi2_sne

    return -0.5*chi2_total

def deltaBIC(samples, n, k):
    params = samples.getParams()
    if hasattr(params, 'chi2'):
        chi2min = np.min(params.chi2)
    elif hasattr(params, 'minuslogpost'):
        chi2min = 2 * np.min(params.minuslogpost)
    else:
        print("Aviso: Chi2 não encontrado nas amostras.")
        return 0

    BIC = chi2min + k*np.log(n)

    return BIC, chi2min