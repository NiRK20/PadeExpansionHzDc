import json
import scripts.modelos as modelos
import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

path_cc = './resultados/P21/CC/resultado_P21_CC.json'
path_pp = './resultados/P21/Pantheon+/resultado_P21_Pantheon+.json'
path_ps = './resultados/P21/Pantheon+&SH0ES/resultado_P21_Pantheon+&SH0ES.json'
path_desi = './resultados/P21/BAO_DESI/resultado_P21_BAO_DESI.json'
path_seb = './resultados/P21/BAO_SeB/resultado_P21_BAO_SeB.json'

paths = [path_cc, path_pp, path_ps, path_desi, path_seb]

resultados = []

for path in paths:
    with open(path) as arquivo:
        resultados.append(json.load(arquivo))

res_cc, res_pp, res_ps, res_desi, res_seb = resultados

z = np.linspace(0, 10, 1000)

def Ez(z, theta):
    h0, Om = theta
    return np.sqrt(Om*(1+z)**3+1-Om)

def um_Ez(z, dc, Om):
    return 1/np.sqrt(Om*(1+z)**3+1-Om)

def DcLCDM(z, theta):
    h0, Om = theta
    sol = solve_ivp(um_Ez, [z[0],z[-1]], [0.0], t_eval=z, args=(Om,), method='RK45')

    return sol.y[0]

par_cc = res_cc['params']
par_pp = res_pp['params']
par_ps = res_ps['params']
par_desi = res_desi['params']
par_seb = res_seb['params']

theta_LCDM = [73.2, 0.33]
theta_cc = [par_cc['M']['media'], par_cc['h0']['media'], par_cc['q0']['media'], par_cc['j0']['media']]
theta_pp = [par_pp['M']['media'], par_pp['h0']['media'], par_pp['q0']['media'], par_pp['j0']['media']]
theta_ps = [par_ps['M']['media'], par_ps['h0']['media'], par_ps['q0']['media'], par_ps['j0']['media']]
theta_desi = [par_desi['M']['media'], par_desi['h0']['media'], par_desi['q0']['media'], par_desi['j0']['media']]
theta_seb = [par_seb['M']['media'], par_seb['h0']['media'], par_seb['q0']['media'], par_seb['j0']['media']]

Dc_P21 = modelos.MODELOS['P21']['Dc']
Ez_P21 = modelos.MODELOS['P21']['Ez']

plt.plot(z, DcLCDM(z, theta_LCDM), label='$\Lambda$CDM')
plt.plot(z, Dc_P21(z, theta_cc), label='CC')
plt.plot(z, Dc_P21(z, theta_pp), label='Pantheon+')
plt.plot(z, Dc_P21(z, theta_ps), label='Pantheon+&SH0ES')
plt.plot(z, Dc_P21(z, theta_desi), label='DESI')
plt.plot(z, Dc_P21(z, theta_seb), label='SeB')
plt.xlabel('$z$')
plt.ylabel('$D_{C}$')
plt.legend()
plt.show()

plt.plot(z, Ez(z, theta_LCDM), label='$\Lambda$CDM')
plt.plot(z, Ez_P21(z, theta_cc), label='CC')
plt.plot(z, Ez_P21(z, theta_pp), label='Pantheon+')
plt.plot(z, Ez_P21(z, theta_ps), label='Pantheon+&SH0ES')
plt.plot(z, Ez_P21(z, theta_desi), label='DESI')
plt.plot(z, Ez_P21(z, theta_seb), label='SeB')
plt.xlabel('$z$')
plt.ylabel('$E$')
plt.ylim(0, 60)
plt.legend()
plt.show()