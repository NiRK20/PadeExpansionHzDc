from getdist import loadMCSamples, plots
import matplotlib.pyplot as plt

path_P21='./scripts/chains/P21/PS/PS_P21'
path_P22='./scripts/chains/P22/PS/PS_P22'
path_P31='./scripts/chains/P31/PS/PS_P31'
path_P32='./scripts/chains/P32/PS/PS_P32'

sample_P21=loadMCSamples(path_P21)
sample_P22=loadMCSamples(path_P22)
sample_P31=loadMCSamples(path_P31)
sample_P32=loadMCSamples(path_P32)

g = plots.getSubplotPlotter()
g.triangle_plot([sample_P21, sample_P22, sample_P31, sample_P32], ['h0', 'q0', 'j0', 's0'], filled=True, legend_labels=['$P_{21}$', '$P_{22}$', '$P_{31}$', '$P_{32}$'], legend_loc='upper right')
g.export('plots_PS_21-32_filled_s0.pdf')
