import json

path_CC = './resultados/P21/CC/resultado_P21_CC.json'
path_PS = './resultados/P21/Pantheons+&SH0ES/resultado_P21_Pantheon+&SH0ES.json'
path_BAO = './resultados/P21/BAO_SeB/resultado_P21_BAO_SeB.json'

resultados = []
paths = [path_CC, path_BAO, path_PS]

for i in range(len(paths)):
    with open(paths[i], 'r') as file:
        resultados.append(json.load(file))

P21_CC, P21_PS, P21_BAO = resultados

for i in list()
