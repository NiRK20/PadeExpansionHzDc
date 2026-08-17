from scripts import modelos
import numpy as np

H0 = 67.4
q0 = -0.5275
j0 = 1.0
rd = 147.1
c = 299792.458

theta_fid = np.array([
    -19.2,  # M: irrelevante para BAO
    H0,
    q0,
    j0
])

escala_bao = c / (H0 * rd)

def Dh_over_rd(z):
    Ez = modelos.MODELOS['P21']['Ez'](z, theta_fid)
    return escala_bao / Ez

def Dm_over_rd(z):
    Dc = modelos.MODELOS['P21']['Dc'](z, theta_fid)
    return escala_bao * Dc

def Dv_over_rd(z):
    return (z * Dh_over_rd(z) * Dm_over_rd(z)**2)**(1/3)

def load_BAO_DESI(arquivo_dados, arquivo_cov):
    dt = np.dtype([('z', 'f8'), ('value', 'f8'), ('quantity', 'U15')])
    zBAO, meanBAO, BAOtype = np.genfromtxt(arquivo_dados, dtype=dt, comments='#', unpack=True)
    cov_mat = np.genfromtxt(arquivo_cov)
    inv_cov = np.linalg.inv(cov_mat)

    return {
        'z': zBAO,
        'mean': meanBAO,
        'type': BAOtype,
        'cov_mat': cov_mat,
        'inv_cov': inv_cov
    }
    
mock_measure = []

dados = load_BAO_DESI('./dados/desi_gaussian_bao_ALL_GCcomb_mean.txt', './dados/desi_gaussian_bao_ALL_GCcomb_cov.txt')

for i in range(len(dados['type'])):
    dtype = dados['type'][i]
    zi = dados['z'][i]
    if dtype == 'DV_over_rs':
        mock_measure.append(Dv_over_rd(zi))
    
    elif dtype == 'DM_over_rs':
        mock_measure.append(Dm_over_rd(zi))
    
    elif dtype == 'DH_over_rs':
        mock_measure.append(Dh_over_rd(zi))

arquivo_mock = './dados/mock_lcdm_bao_mean.txt'

if len(mock_measure) != len(dados['z']):
    raise ValueError('O vetor mock não possui o mesmo tamanho dos dados DESI.')

with open(arquivo_mock, 'w') as arquivo:
    arquivo.write('# [z] [value at z] [quantity]\n')

    for z, valor, tipo in zip(
        dados['z'],
        mock_measure,
        dados['type']
    ):
        arquivo.write(f'{z:.8f} {valor:.12f} {tipo}\n')

print(f'Mock salvo em: {arquivo_mock}')

mock_data = load_BAO_DESI(
    './dados/mock_lcdm_bao_mean.txt',
    './dados/desi_gaussian_bao_ALL_GCcomb_cov.txt'
)

print(mock_data['mean'])
print(mock_data['type'])