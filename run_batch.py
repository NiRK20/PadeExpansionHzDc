import subprocess
import time
import os
import sys
import threading
from datetime import datetime, timedelta

# --- CONFIGURAÇÃO ---
DIRETORIO_DO_CODIGO = "./scripts" 
PASTA_RELATORIOS = "./relatorios"
ARQUIVO_STATUS_TEMP = "status_running.txt" # O arquivo que você vai vigiar

# Lista de tarefas
tarefas = [
    {"modelo": "P21", "sh0es": True, "nlive": 250},
    #{"modelo": "P22", "sh0es": True, "nlive": 300},
    #{"modelo": "P31", "sh0es": True, "nlive": 300},
    #{"modelo": "P32", "sh0es": True, "nlive": 350},
]

# --- VARIÁVEIS GLOBAIS PARA O MONITOR ---
g_job_atual = "Iniciando..."
g_start_time = time.time()
g_stop_event = threading.Event() # Bandeira para parar o monitor

def formatar_tempo(segundos):
    return str(timedelta(seconds=int(segundos)))

def thread_monitoramento():
    """
    Função que roda em paralelo. Ela acorda a cada 1s,
    calcula o tempo e sobrescreve o arquivo de status.
    """
    while not g_stop_event.is_set():
        tempo_decorrido = time.time() - g_start_time
        tempo_str = formatar_tempo(tempo_decorrido)
        
        try:
            with open(ARQUIVO_STATUS_TEMP, "w") as f:
                f.write(f"--- MONITORAMENTO EM TEMPO REAL ---\n")
                f.write(f"Atualização: {datetime.now().strftime('%H:%M:%S')}\n")
                f.write(f"-----------------------------------\n")
                f.write(f"MODELO ATUAL : {g_job_atual}\n")
                f.write(f"TEMPO RODANDO: {tempo_str}\n")
                f.write(f"-----------------------------------\n")
                f.write(f"(Use 'watch -n 1 cat {ARQUIVO_STATUS_TEMP}' para acompanhar)\n")
        except:
            pass # Ignora erros de escrita se o arquivo estiver travado rapidinho
            
        time.sleep(1) # Atualiza a cada 1 segundo

def rodar_comando(modelo, usar_shoes, nlive, diretorio_alvo):
    # Atualiza as variáveis globais para o monitor pegar
    global g_job_atual, g_start_time
    tag_shoes = "COM_SHOES" if usar_shoes else "SEM_SHOES"
    g_job_atual = f"{modelo} [{tag_shoes}]"
    g_start_time = time.time()
    
    # Monta o comando
    cmd = [sys.executable, "run_cobaya.py", "--run", "--modelo", modelo, "--nlive", str(nlive)]
    if usar_shoes:
        cmd.append("--sh0es")

    # Configura ambiente para evitar travamento do PolyChord
    env = os.environ.copy()
    env["OMP_NUM_THREADS"] = "1"
    env["MPI_NUM_PROCESSES"] = "1"
    env["PC_NO_MPI"] = "1"

    print(f"\n{'#'*60}")
    print(f"DISPARANDO: {g_job_atual}")
    print(f"{'#'*60}\n")

    try:
        # Roda direto no terminal (sem capturar stdout/stderr)
        # Isso evita o buffer deadlock. O output vai aparecer na tela.
        subprocess.run(cmd, check=True, cwd=diretorio_alvo, env=env)
        return True
    except subprocess.CalledProcessError:
        print(f"\n!!! ERRO NO MODELO {g_job_atual} !!!\n")
        return False
    except Exception as e:
        print(f"\n!!! ERRO GERAL: {e}\n")
        return False

# --- MAIN ---
if __name__ == "__main__":
    if not os.path.exists(PASTA_RELATORIOS): os.makedirs(PASTA_RELATORIOS)
    if not os.path.exists(DIRETORIO_DO_CODIGO):
        print(f"Diretório {DIRETORIO_DO_CODIGO} não encontrado.")
        sys.exit(1)

    # 1. Inicia a Thread de Monitoramento
    monitor = threading.Thread(target=thread_monitoramento, daemon=True)
    monitor.start()

    inicio_geral = time.time()
    data_inicio = datetime.now().strftime('%d/%m/%Y %H:%M')
    
    lista_sucessos = []
    lista_falhas = []

    try:
        # 2. Loop de Tarefas
        for job in tarefas:
            sucesso = rodar_comando(job["modelo"], job["sh0es"], job["nlive"], DIRETORIO_DO_CODIGO)
            
            nome_job = f"{job['modelo']} ({'SH0ES' if job['sh0es'] else 'NO_SH0ES'})"
            if sucesso:
                lista_sucessos.append(nome_job)
            else:
                lista_falhas.append(nome_job)
                
    except KeyboardInterrupt:
        print("\n\n!!! INTERROMPIDO PELO USUÁRIO !!!\n")
        
    finally:
        # 3. Limpeza Final (roda mesmo se der erro)
        g_stop_event.set() # Para o monitor
        monitor.join()     # Espera a thread morrer
        
        if os.path.exists(ARQUIVO_STATUS_TEMP):
            os.remove(ARQUIVO_STATUS_TEMP) # Deleta o log temporário
            print(f"\nArquivo temporário {ARQUIVO_STATUS_TEMP} removido.")

        # 4. Relatório Permanente
        tempo_total = (time.time() - inicio_geral) / 3600
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
        
        relatorio = [
            "="*60,
            f"RELATÓRIO FINAL DE BATCH",
            f"Data: {timestamp}",
            "="*60,
            f"Tempo Total: {tempo_total:.2f} horas",
            f"Sucessos: {len(lista_sucessos)}",
            f"Falhas:   {len(lista_falhas)}",
            "-"*60
        ]
        
        if lista_sucessos:
            relatorio.append("SUCESSOS:")
            for s in lista_sucessos: relatorio.append(f" [V] {s}")
            
        if lista_falhas:
            relatorio.append("\nFALHAS:")
            for f in lista_falhas: relatorio.append(f" [X] {f}")
            
        relatorio.append("="*60)
        texto_final = "\n".join(relatorio)
        
        print("\n" + texto_final + "\n")
        
        caminho_rel = os.path.join(PASTA_RELATORIOS, f"resumo_{timestamp}.txt")
        with open(caminho_rel, "w") as f:
            f.write(texto_final)
            
        print(f"Relatório salvo em: {caminho_rel}")
