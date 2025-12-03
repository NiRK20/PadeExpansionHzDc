import subprocess
from subprocess import DEVNULL
import time
from datetime import datetime, timedelta
import os
import sys

PASTA_LOGS = "./logs"
PASTA_RELATORIOS = "./relatorios"

tarefas = [
    #{"modelo": "P21", "sh0es": False, "nlive": 250},
    {"modelo": "P22", "sh0es": False, "nlive": 300},
    #{"modelo": "P31", "sh0es": False, "nlive": 300},
    #{"modelo": "P32", "sh0es": False, "nlive": 350},
    {"modelo": "P21", "sh0es": True, "nlive": 250},
    {"modelo": "P22", "sh0es": True, "nlive": 300},
    {"modelo": "P31", "sh0es": True, "nlive": 300},
    {"modelo": "P32", "sh0es": True, "nlive": 350},
]

def formatar_tempo(segundos):
    return str(timedelta(seconds=int(segundos)))

def run_command(modelo, nlive, sh0es, n_sim, n_tot, pasta_sessao, tempo_inicio_global):
    
    cmd = ["python3", "-u", "run_cobaya.py", "--run", "--modelo", modelo, "--nlive", str(nlive)]
    tag_sh0es = False

    if sh0es:
        cmd.append("--sh0es")
        tag_sh0es = True

    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')

    nome_log = f"log_{modelo}_{tag_sh0es}_{timestamp}.txt"
    caminho_log = os.path.abspath(os.path.join(pasta_sessao, nome_log))

    tempo_decorrido = time.time() - tempo_inicio_global
    tempo_str = formatar_tempo(tempo_decorrido)

    comando_shell = (
        f"cd {diretorio_alvo} && "  # Entra na pasta
        f"export OMP_NUM_THREADS=1 && " # Trava threads para evitar conflito
        f"export MPI_NUM_PROCESSES=1 && "
        f"export MKL_NUM_THREADS=1 && "
        f"export POLYCHORD_NO_MPI=1 && "
        f"{sys.executable} -u run_cobaya.py " # Chama o Python correto
        f"--run --modelo {modelo} --nlive {nlive} {tag_sh0es} " # Argumentos
        f"> {caminho_log} 2>&1" # Redireciona tudo para o arquivo (Linux cuida disso)
    )

    print(f"\n{'#'*30}", flush=True)
    print(f"# Iniciando simulação do modelo {modelo} [{tag_sh0es}]", flush=True)
    print(f"# Hora: {datetime.now().strftime('%H:%M:%S')}", flush=True)
    print(f"# Log sendo salvo em {caminho_log}", flush=True)
    print(f"{'#'*30}\n", flush=True)

    with open(caminho_log, "w") as f_head:
        f_head.write(f"--- SIMULAÇÃO {modelo} {tag_shoes} ---\n")
        f_head.write(f"Inicio: {datetime.now()}\n")
        f_head.write(f"Comando Real: {comando_shell}\n")
        f_head.write("-" * 50 + "\n")

    codigo_saida = os.system(comando_shell)

    if codigo_saida == 0:
        print(f">>> SUCESSO: {modelo} finalizado.", flush=True)
        return True
    else:
        print(f"!!! FALHA: {modelo} retornou código {codigo_saida}. Veja o log.", flush=True)
        # Registra falha no fim do log
        with open(caminho_log, "a") as f_end:
            f_end.write(f"\n!!! ERRO: Processo morreu com código {codigo_saida} !!!\n")
        return False

    try:
        comando_shell = f"{' '.join(cmd)} > {caminho_log} 2>&1"
        
        # Escrevemos o cabeçalho manualmente antes de rodar
        with open(caminho_log, "w") as f_head:
            f_head.write(f"--- SIMULAÇÃO {modelo} {tag_sh0es} ---\n")
            f_head.write(f"Inicio: {datetime.now()}\n")
            f_head.write(f"Comando Shell: {comando_shell}\n")
            f_head.write("-" * 50 + "\n")

            # A MÁGICA: stdout e stderr vão direto para o arquivo f_log
            subprocess.run(
            comando_shell, 
            check=True, 
            cwd="./scripts", 
            shell=True,             # <--- Importante
            env=env_personalizado
        )
        print(f"\n>>> Simulação {n_sim} de {n_tot} concluída coim sucesso.\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n ERROR: {modelo} [SH0ES={tag_sh0es}] falhou com código {e.returncode}. Avançando para a próxima simulação.\n")
        with open(caminho_log, "a") as f_log:
            f_log.write(f"\n ERROR: {modelo} [SH0ES={tag_sh0es}] falhou com código {e.returncode}. Avançando para a próxima simulação.\n")
        return False
    except Exception as e:
        print(f"\nERROR: {e}\n")
        with open(caminho_log, "a") as f_log:
            f_log.write(f"\n ERROR: {modelo} [SH0ES={tag_sh0es}] falhou com código {e}. Avançando para a próxima simulação.\n")
        return False

if __name__ == "__main__":    
    if not os.path.exists(PASTA_LOGS):
        os.makedirs(PASTA_LOGS)
    if not os.path.exists(PASTA_RELATORIOS):
        os.makedirs(PASTA_RELATORIOS)
    
    inicio_total = time.time()

    timestamp_sessao = datetime.now().strftime('%Y-%m-%d_%H-%M')    
    pasta_sessao = os.path.join(PASTA_LOGS, timestamp_sessao)
    if not os.path.exists(pasta_sessao):
        os.makedirs(pasta_sessao)

    print(f"--- BATCH RUN INICIADO ---")
    print(f"Logs desta rodada serão salvos em: {os.path.abspath(pasta_sessao)}\n", flush=True)
    
    data_inicio = datetime.now().strftime('%d/%m/%Y %H:%M')
    sucessos = []
    falhas = []

    i = 1
    for sim in tarefas:
        simulation = f"{sim["modelo"]} (SH0ES={sim["sh0es"]})"
        sucesso = run_command(sim["modelo"], sim["nlive"], sim["sh0es"], i, len(tarefas), pasta_sessao, inicio_total)
        i += 1

        if sucesso:
            sucessos.append(simulation)
        else:
            falhas.append(simulation)

    tempo_total = (time.time() - inicio_total) / 60
    data_fim = datetime.now().strftime('%d-%m-%Y_%H-%M') # Formato seguro para nome de arquivo
    
    # --- CONSTRUÇÃO DO RELATÓRIO (STRING) ---
    relatorio = []
    relatorio.append("-"*60)
    relatorio.append(f"RELATÓRIO FINAL DE EXECUÇÃO EM LOTE")
    relatorio.append(f"Data: {timestamp_sessao}")
    relatorio.append(f"Pasta de Logs: {os.path.abspath(pasta_sessao)}")
    relatorio.append("-"*60 + "\n")
    
    relatorio.append(f"Tempo Total: {tempo_total:.2f} horas")
    relatorio.append(f"Total de Tarefas: {len(tarefas)}")
    relatorio.append(f"Sucessos: {len(sucessos)}")
    relatorio.append(f"Falhas:   {len(falhas)}\n")
    
    if len(sucessos) > 0:
        relatorio.append("--- LISTA DE SUCESSOS ---")
        for s in sucessos:
            relatorio.append(f"[V] {s}")
        relatorio.append("")

    if len(falhas) > 0:
        relatorio.append("--- LISTA DE FALHAS (VERIFICAR LOGS) ---")
        for f in falhas:
            relatorio.append(f"[X] {f}")
        relatorio.append("")
    
    relatorio.append("-" * 60)
    if len(falhas) == 0:
        relatorio.append("RESULTADO: SUCESSO TOTAL.")
    else:
        relatorio.append("RESULTADO: HOUVE ERROS.")
    relatorio.append("-"*60)

    # Junta tudo numa única string
    texto_final = "\n".join(relatorio)

    # Salva no arquivo .txt
    nome_arquivo = f"relatorio_batch_{data_fim}.txt"
    caminho_completo_relatorio = os.path.join(PASTA_RELATORIOS, nome_arquivo)
    with open(caminho_completo_relatorio, "w") as f:
        f.write(texto_final)
    with open(os.path.join(pasta_sessao, "_RESUMO.txt"), "w") as f:
        f.write(texto_final)
        
    print(f">>> Relatório salvo em: {os.path.abspath(caminho_completo_relatorio)}")