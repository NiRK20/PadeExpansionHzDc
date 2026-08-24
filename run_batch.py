import subprocess, time, os, sys, threading
from datetime import datetime, timedelta

PATH_CODIGOS = './scripts/motor'
PATH_RELATORIOS = './relatorios'
ARQUIVO_STATUS = 'status.txt'

SEED = 42
P21_NLIVE = 100
P22_NLIVE = 150

tarefas = [
    {'modelo': 'P31', 'dados': ['cc', 'sne', 'bao_seb'], 'sh0es': True, 'nlive': P22_NLIVE, 'seed': SEED, 'mock': 'P31'},
    {'modelo': 'P31', 'dados': ['cc', 'sne', 'bao_desi'], 'sh0es': True, 'nlive': P22_NLIVE, 'seed': SEED, 'mock': 'P31'},
    {'modelo': 'P31', 'dados': ['cc', 'sne', 'bao_seb'], 'sh0es': True, 'nlive': P22_NLIVE, 'seed': SEED, 'mock': 'LCDM'},
    {'modelo': 'P31', 'dados': ['cc', 'sne', 'bao_desi'], 'sh0es': True, 'nlive': P22_NLIVE, 'seed': SEED, 'mock': 'LCDM'}
]

job_atual = 'Iniciando...'
job_start_time = time.time()
job_stop_event = threading.Event()

def formatar_tempo(segundos):
    return str(timedelta(seconds=int(segundos)))

def thread_monitoramento():
    '''Função que roda em paralelo, atualizando o arquivo status.txt
    a cada 1 segundo.'''

    while not job_stop_event.is_set():
        tempo_passado = time.time() - job_start_time
        tempo_str = formatar_tempo(tempo_passado)

        try:
            with open(ARQUIVO_STATUS, 'w') as file:
                file.write(f'--- MONITORAMENTE EM TEMPO REAL ---\n')
                file.write(f'Atualização: {datetime.now().strftime("%H:%M:%S")}\n')
                file.write(20*'-')
                file.write(f'\nMODELO ATUAL: {job_atual}\n')
                file.write(f'TEMPO RODANDO: {tempo_str}\n')
                file.write(20*'-')
                # Use 'watch -n 1 cat status.txt' para acompanhar
        except:
            pass

        time.sleep(1)

def rodar_comando(modelo, dados, sh0es, nlive, seed, mock, diretorio):
    global job_atual, job_start_time

    job_atual = f'{modelo} com {dados} (SH0ES={sh0es})'
    job_start_time = time.time()

    cmd = [sys.executable, 'run_cobaya.py', '--run', '--modelo', modelo, '--nlive', str(nlive), '--seed', str(seed), '--mock', str(mock)]
    if sh0es:
        cmd.append('--sh0es')
    
    cmd.append('--dados')
    for dado in dados:
        cmd.append(dado)
    
    env = os.environ.copy()
    env["OMP_NUM_THREADS"] = "1"
    env["MPI_NUM_PROCESSES"] = "1"
    env["PC_NO_MPI"] = "1"
    print(f"\n{'#'*60}")
    print(f"DISPARANDO: {job_atual}")
    print(f"{'#'*60}\n")

    try:
        subprocess.run(cmd, check=True, cwd=diretorio, env=env)
        return True
    except subprocess.CalledProcessError:
        print(f"\n!!! ERRO NO MODELO {job_atual} !!!\n")
        return False
    except Exception as e:
        print(f"\n!!! ERRO GERAL: {e}\n")
        return False
    
if __name__ == '__main__':
    if not os.path.exists(PATH_RELATORIOS): os.makedirs(PATH_RELATORIOS)
    if not os.path.exists(PATH_CODIGOS):
        print(f'Diretório {PATH_CODIGOS} dos códigos não encontrado...')
        sys.exit(1)
    
    monitor = threading.Thread(target=thread_monitoramento, daemon=True)
    monitor.start()

    inicio = time.time()
    data = datetime.now().strftime('%d/%m/%Y %H%M')

    lista_sucessos = []
    lista_fracassos = []

    try:
        for job in tarefas:
            sucesso = rodar_comando(job['modelo'], job['dados'], job['sh0es'], job['nlive'], job['seed'], job['mock'], PATH_CODIGOS)

            nome_job = f"{job['modelo']} ({job['dados']})"
            if sucesso:
                lista_sucessos.append(nome_job)
            else:
                lista_fracassos.append(nome_job)
    except KeyboardInterrupt:
        print("\n\n!!! INTERROMPIDO PELO USUÁRIO !!!\n")
    
    finally:
        job_stop_event.set()
        monitor.join()

        if os.path.exists(ARQUIVO_STATUS):
            os.remove(ARQUIVO_STATUS)
            print(f'\nArquivo temporário de status {ARQUIVO_STATUS} removido.')
        
        tempo_total = (time.time() - inicio)/3600
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')

        relatorio = [
            '='*60,
            'RELATÓRIO FINAL DE BATCH',
            f'Data: {timestamp}',
            '-'*60,
            f'Tempo total: {tempo_total:.2f} horas',
            f'Sucessos: {len(lista_sucessos)}',
            f'Fracassos: {len(lista_fracassos)}',
        ]
        
        if lista_sucessos:
            relatorio.append("SUCESSOS:")
            for s in lista_sucessos: relatorio.append(f" [V] {s}")
            
        if lista_fracassos:
            relatorio.append("\nFALHAS:")
            for f in lista_fracassos: relatorio.append(f" [X] {f}")
            
        relatorio.append("="*60)
        texto_final = "\n".join(relatorio)
        
        print("\n" + texto_final + "\n")
        
        caminho_rel = os.path.join(PATH_RELATORIOS, f"resumo_{timestamp}.txt")
        with open(caminho_rel, "w") as f:
            f.write(texto_final)
            
        print(f"Relatório salvo em: {caminho_rel}")
