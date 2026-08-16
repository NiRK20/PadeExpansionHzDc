import json
import scripts.modelos as modelos
import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt

path_ps_desi = './resultados/P21/CC+Pantheon+&SH0ES+BAO_DESI/resultado_P21_CC+Pantheon+&SH0ES+BAO_DESI.json'
path_ps_seb = './resultados/P21/CC+Pantheon+&SH0ES+BAO_SeB/resultado_P21_CC+Pantheon+&SH0ES+BAO_SeB.json'
path_pp_desi = './resultados/P21/CC+Pantheon++BAO_DESI/resultado_P21_CC+Pantheon++BAO_DESI.json'
path_pp_seb = './resultados/P21/CC+Pantheon++BAO_SeB/resultado_P21_CC+Pantheon++BAO_SeB.json'

paths = [path_ps_desi, path_ps_seb, path_pp_desi, path_pp_seb]

resultados = []

for path in paths:
    with open(path) as arquivo:
        resultados.append(json.load(arquivo))

res_ps_desi, res_ps_seb, res_pp_desi, res_pp_seb = resultados

z_max = 10
z = np.linspace(0, z_max, 1000)

def Ez(z, theta):
    h0, Om = theta
    return np.sqrt(Om*(1+z)**3+1-Om)

def um_Ez(z, dc, Om):
    return 1/np.sqrt(Om*(1+z)**3+1-Om)

def DcLCDM(z, theta):
    h0, Om = theta
    sol = solve_ivp(um_Ez, [z[0],z[-1]], [0.0], t_eval=z, args=(Om,), method='RK45')

    return sol.y[0]

par_ps_desi = res_ps_desi['params']
par_ps_seb = res_ps_seb['params']
par_pp_desi = res_pp_desi['params']
par_pp_seb = res_pp_seb['params']

theta_LCDM = [73.2, 0.33]
theta_ps_desi = [par_ps_desi['M']['media'], par_ps_desi['h0']['media'], par_ps_desi['q0']['media'], par_ps_desi['j0']['media']]
theta_ps_seb = [par_ps_seb['M']['media'], par_ps_seb['h0']['media'], par_ps_seb['q0']['media'], par_ps_seb['j0']['media']]
theta_pp_desi = [par_pp_desi['M']['media'], par_pp_desi['h0']['media'], par_pp_desi['q0']['media'], par_pp_desi['j0']['media']]
theta_pp_seb = [par_pp_seb['M']['media'], par_pp_seb['h0']['media'], par_pp_seb['q0']['media'], par_pp_seb['j0']['media']]

Dc_P21 = modelos.MODELOS['P21']['Dc']
Ez_P21 = modelos.MODELOS['P21']['Ez']

plt.plot(z, DcLCDM(z, theta_LCDM), label='$\Lambda$CDM')
plt.plot(z, Dc_P21(z, theta_ps_desi), label='CC+Pantheon+&SH0ES+DESI')
plt.plot(z, Dc_P21(z, theta_ps_seb), label='CC+Pantheon+&SH0ES+SeB')
plt.plot(z, Dc_P21(z, theta_pp_desi), label='CC+Pantheon++DESI')
plt.plot(z, Dc_P21(z, theta_pp_seb), label='CC+Pantheon++SeB')
plt.xlabel('$z$')
plt.ylabel('$D_{C}$')
plt.legend()
plt.show()

plt.plot(z, Ez(z, theta_LCDM), label='$\Lambda$CDM')
plt.plot(z, Ez_P21(z, theta_ps_desi), label='CC+Pantheon+&SH0ES+DESI')
plt.plot(z, Ez_P21(z, theta_ps_seb), label='CC+Pantheon+&SH0ES+SeB')
plt.plot(z, Ez_P21(z, theta_pp_desi), label='CC+Pantheon++DESI')
plt.plot(z, Ez_P21(z, theta_pp_seb), label='CC+Pantheon++SeB')
plt.xlabel('$z$')
plt.ylabel('$E$')
plt.ylim(0, 60)
plt.legend()
plt.show()