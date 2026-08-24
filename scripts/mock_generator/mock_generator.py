import numpy as np
from scripts.motor import data_loader, modelos
from scipy.integrate import quad
from pathlib import Path
import pandas as pd

H0 = 67.4 # km/s/Mpc
Om = 0.315
c =  299792.458 # km/s

VALFID = {
    'H0': H0,
    'Om': Om,
    'c': c,
    'rd': 147.1, # Mpc
    'M': -19.25,
    'dH': c / H0,
    'q0': (3 / 2) * Om - 1,
    'j0': 1,
    's0': 1 - (9 / 2) * Om
}

THETA = {
    'LCDM': VALFID['Om'],
    'P21': (VALFID['M'], VALFID['H0'], VALFID['q0'], VALFID['j0']),
    'P22': (VALFID['M'], VALFID['H0'], VALFID['q0'], VALFID['j0'], VALFID['s0']),
    'P31': (VALFID['M'], VALFID['H0'], VALFID['q0'], VALFID['j0'], VALFID['s0'])
}

PATH_FOLDER = Path(__file__).resolve().parent.parent.parent / 'dados'
PATH_FOLDER_MOCK = Path(__file__).resolve().parent.parent.parent / 'mock_data'

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

def EzLCDM(z, Om):
    return np.sqrt(Om * (1 + z)**3 + 1 - Om)


def DcLCDM_scalar(z, theta):
    dc, _ = quad(lambda zi, thetai: 1/EzLCDM(zi, thetai), 0, z, args=(theta,))
    return dc


DcLCDM = np.vectorize(DcLCDM_scalar)


def Dh(z, Ez, theta):
    return VALFID['dH']/Ez(z, theta)


def Dm(z, Dc, theta):
    return VALFID['dH'] * Dc(z, theta)


def Da(z, Dc, theta):
    return Dm(z, Dc, theta)/(1 + z)


def Dv(z, Dc, Ez, theta):
    return (z * Dm(z, Dc, theta)**2 * Dh(z, Ez, theta))**(1 / 3)


MODELOS = {
    'LCDM': {
        'name': 'LCDM',
        'Ez': EzLCDM,
        'Dc': DcLCDM
    },

    'P21': {
        'name': modelos.MODELOS['P21']['modelo'],
        'Ez': modelos.MODELOS['P21']['Ez'],
        'Dc': modelos.MODELOS['P21']['Dc']
    },

    'P22': {
        'name': modelos.MODELOS['P22']['modelo'],
        'Ez': modelos.MODELOS['P22']['Ez'],
        'Dc': modelos.MODELOS['P22']['Dc']
    },

    'P31': {
        'name': modelos.MODELOS['P31']['modelo'],
        'Ez': modelos.MODELOS['P31']['Ez'],
        'Dc': modelos.MODELOS['P31']['Dc']
    }
}


cc_data = data_loader.load_cronometros(PATH_DATA['CC'], PATH_COV['CC'], mock=False)
ps_data = data_loader.load_supernovas(PATH_DATA['SNe'], PATH_COV['SNe'], sh0es=True)
pp_data = data_loader.load_supernovas(PATH_DATA['SNe'], PATH_COV['SNe'], sh0es=False)
desi_data = data_loader.load_BAO_DESI(PATH_DATA['DESI'], PATH_COV['DESI'])
seb_data = data_loader.load_BAO_SeB(PATH_DATA['SeB'])


def create_mock(dtype, model):
    PATH = PATH_FOLDER_MOCK / f'{model["name"]}'
    PATH.mkdir(parents=True, exist_ok=True)
    match dtype:
        case 'cc':
            print(f'GERANDO DADOS DE CC DO MODELO {model["name"]}')
            cc_Hz_mock = VALFID['H0'] * model['Ez'](cc_data['z'], THETA[model['name']])
            
            cc_raw = np.genfromtxt(PATH_DATA['CC'], comments='#', dtype=str)
            cc_raw[:, 1] = [f'{valor:.8f}' for valor in cc_Hz_mock]
            np.savetxt(PATH / f'33CC_mock_{model["name"]}.dat', cc_raw, fmt='%s', header='z Hz errHz M')

        case 'sne':
            print(f'GERANDO DADOS DE SNe DO MODELO {model["name"]}')
            sne_mock = pd.read_csv(PATH_DATA['SNe'], sep=r'\s+')
            z_hd = sne_mock['zHD'].to_numpy()
            z_hel = sne_mock['zHEL'].to_numpy()
            is_calibrator = sne_mock['IS_CALIBRATOR'].astype(bool).to_numpy()
            
            m_mock = 5 * np.log10((1 + z_hd) * (1 + z_hel) * Da(z_hd, model['Dc'], THETA[model['name']])) + 25 + VALFID['M']
            m_mock[is_calibrator] = sne_mock.loc[is_calibrator, 'CEPH_DIST'].to_numpy() + VALFID['M']
            
            sne_mock['m_b_corr'] = m_mock
            
            sne_mock.to_csv(PATH / f'Pantheon+SH0ES_mock_{model["name"]}.dat', sep=' ', index=False)

        case 'desi':
            print(f'GERANDO DADOS DE BAO DO DESI DO MODELO {model["name"]}')
            desi_mock = []
            for i in range(len(desi_data['type'])):
                dtype = desi_data['type'][i]
                zi = desi_data['z'][i]
                
                if dtype == 'DV_over_rs':
                    desi_mock.append(Dv(zi, model['Dc'], model['Ez'], THETA[model['name']])/VALFID['rd'])
                elif dtype == 'DM_over_rs':
                    desi_mock.append(Dm(zi, model['Dc'], THETA[model['name']])/VALFID['rd'])
                elif dtype == 'DH_over_rs':
                    desi_mock.append(Dh(zi, model['Ez'], THETA[model['name']])/VALFID['rd'])

            with open(PATH / f'desi_mean_mock_{model["name"]}.txt', 'w') as arquivo:
                arquivo.write('# [z] [value at z] [quantity]\n')
            
                for z, valor, tipo in zip(
                    desi_data['z'],
                    desi_mock,
                    desi_data['type']
                ):
                    arquivo.write(f'{z:.8f} {valor:.12f} {tipo}\n')

        case 'seb':
            print(f'GERANDO DADOS DE BAO DE SEB DO MODELO {model["name"]}')
            seb_mock = (VALFID['dH'] / VALFID['rd']) * (model['Dc'](seb_data['z'], THETA[model['name']]) / (1 + seb_data['z']))
            
            seb_raw = np.genfromtxt(PATH_DATA['SeB'])
            seb_raw[:, 1] = seb_mock
            np.savetxt(PATH / f'Da_rd18_mock_{model["name"]}.txt', seb_raw, fmt='%.12f')

        case _:
            print('TIPO DE DADO INVÁLIDO')

    print('DADOS GERADOS\n')

for modelo in MODELOS:
    create_mock('cc', MODELOS[modelo])
    create_mock('sne', MODELOS[modelo])
    create_mock('desi', MODELOS[modelo])
    create_mock('seb', MODELOS[modelo])