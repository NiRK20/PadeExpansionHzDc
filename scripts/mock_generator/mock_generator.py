import numpy as np
from scripts.motor import data_loader
from scipy.integrate import quad
from pathlib import Path
import pandas as pd

VALFID = {
    'H0': 67.4, # km/s/Mpc
    'Om': 0.315,
    'rd': 147.1, # Mpc
    'c': 299792.458, # km/s
    'M': -19.25,
    'dH': 299792.458 / 67.4
}

PATH_FOLDER = Path(__file__).resolve().parent.parent.parent / 'dados'
PATH_FOLDER_MOCK = Path(__file__).resolve().parent.parent.parent / 'mock_data' / 'LCDM'

PATH_FOLDER_MOCK.mkdir(parents=True, exist_ok=True)

PATH_DATA = {
    'CC': PATH_FOLDER / '33CCdata.dat',
    'SNe': PATH_FOLDER / 'Pantheon+SH0ES.dat',
    'DESI': PATH_FOLDER / 'desi_gaussian_bao_ALL_GCcomb_mean.txt',
    'SeB': PATH_FOLDER / 'DA_rd18.txt'
}

PATH_COV = {
    'CC': PATH_FOLDER / 'data_MM20.dat',
    'SNe': PATH_FOLDER / 'Pantheon+SH0ES_STAT+SYS.cov',
    'DESI': PATH_FOLDER / 'desi_gaussian_bao_ALL_GCcomb_cov.txt'
}

def EzLCDM(z):
    return np.sqrt(VALFID['Om'] * (1 + z)**3 + 1 - VALFID['Om'])


def DcLCDM_scalar(z):
    dc, _ = quad(lambda zi: 1/EzLCDM(zi), 0, z)
    return dc


DcLCDM = np.vectorize(DcLCDM_scalar)


def DhLCDM(z):
    return VALFID['dH']/EzLCDM(z)


def DmLCDM(z):
    return VALFID['dH'] * DcLCDM(z)


def DaLCDM(z):
    return DmLCDM(z)/(1 + z)


def DvLCDM(z):
    return (z * DmLCDM(z)**2 * DhLCDM(z))**(1 / 3)


cc_data = data_loader.load_cronometros(PATH_DATA['CC'], PATH_COV['CC'])
ps_data = data_loader.load_supernovas(PATH_DATA['SNe'], PATH_COV['SNe'], sh0es=True)
pp_data = data_loader.load_supernovas(PATH_DATA['SNe'], PATH_COV['SNe'], sh0es=False)
desi_data = data_loader.load_BAO_DESI(PATH_DATA['DESI'], PATH_COV['DESI'])
seb_data = data_loader.load_BAO_SeB(PATH_DATA['SeB'])


print('GERANDO DADOS DE CC')
cc_Hz_mock = VALFID['H0'] * EzLCDM(cc_data['z'])

cc_raw = np.genfromtxt(PATH_DATA['CC'], comments='#', dtype=str)
cc_raw[:, 1] = [f'{valor:.8f}' for valor in cc_Hz_mock]
np.savetxt(PATH_FOLDER_MOCK / '33CC_mock_LCDM.dat', cc_raw, fmt='%s', header='z Hz errHz M')


print('GERANDO DADOS DE SNe')
sne_mock = pd.read_csv(PATH_DATA['SNe'], sep=r'\s+')
z_hd = sne_mock['zHD'].to_numpy()
z_hel = sne_mock['zHEL'].to_numpy()
is_calibrator = sne_mock['IS_CALIBRATOR'].astype(bool).to_numpy()

m_mock = 5 * np.log10((1 + z_hd) * (1 + z_hel) * DaLCDM(z_hd)) + 25 + VALFID['M']
m_mock[is_calibrator] = sne_mock.loc[is_calibrator, 'CEPH_DIST'].to_numpy() + VALFID['M']

sne_mock['m_b_corr'] = m_mock

sne_mock.to_csv(PATH_FOLDER_MOCK / 'Pantheon+SH0ES_mock_LCDM.dat', sep=' ', index=False)


print('GERANDO DADOS DE BAO DO DESI')
desi_mock = []
for i in range(len(desi_data['type'])):
    dtype = desi_data['type'][i]
    zi = desi_data['z'][i]
    
    if dtype == 'DV_over_rs':
        desi_mock.append(DvLCDM(zi)/VALFID['rd'])
    elif dtype == 'DM_over_rs':
        desi_mock.append(DmLCDM(zi)/VALFID['rd'])
    elif dtype == 'DH_over_rs':
        desi_mock.append(DhLCDM(zi)/VALFID['rd'])


with open(PATH_FOLDER_MOCK / 'desi_mean_mock_LCDM.txt', 'w') as arquivo:
    arquivo.write('# [z] [value at z] [quantity]\n')

    for z, valor, tipo in zip(
        desi_data['z'],
        desi_mock,
        desi_data['type']
    ):
        arquivo.write(f'{z:.8f} {valor:.12f} {tipo}\n')


print('GERANDO DADOS DE BAO DE SEB')
seb_mock = (VALFID['dH'] / VALFID['rd']) * (DcLCDM(seb_data['z']) / (1 + seb_data['z']))

seb_raw = np.genfromtxt(PATH_DATA['SeB'])
seb_raw[:, 1] = seb_mock
np.savetxt(PATH_FOLDER_MOCK / 'Da_rd18_mock_LCDM.txt', seb_raw, fmt='%.12f')