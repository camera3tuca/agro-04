"""
Sistema de Jobs Agendados
Executa tarefas em background e mantém dados atualizados
"""

import schedule
import time
import threading
from datetime import datetime, timedelta
from typing import Callable, List, Dict, Optional
import json
from pathlib import Path

class SchedulerManager:
    """Gerenciador de tarefas agendadas"""
    
    def __init__(self, config_file: str = ".scheduler/config.json"):
        """
        Inicializa o gerenciador de agendamento
        
        Args:
            config_file: Arquivo de configuração
        """
        self.config_file = Path(config_file)
        self.config_file.parent.mkdir(exist_ok=True)
        
        self.jobs = []
        self.is_running = False
        self.thread = None
        
        # Log de execuções
        self.log_file = self.config_file.parent / "scheduler_log.json"
        self.execution_log = self._load_log()
    
    def _load_log(self) -> List[Dict]:
        """Carrega log de execuções"""
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _save_log(self):
        """Salva log de execuções"""
        try:
            # Mantém apenas últimos 1000 registros
            log_to_save = self.execution_log[-1000:]
            
            with open(self.log_file, 'w') as f:
                json.dump(log_to_save, f, indent=2, default=str)
        except Exception as e:
            print(f"Erro ao salvar log: {e}")
    
    def _log_execution(self, job_name: str, status: str, duration: float, error: Optional[str] = None):
        """Registra execução de job"""
        log_entry = {
            'job_name': job_name,
            'timestamp': datetime.now().isoformat(),
            'status': status,
            'duration_seconds': duration,
            'error': error
        }
        
        self.execution_log.append(log_entry)
        self._save_log()
    
    def add_job(self, 
                func: Callable, 
                schedule_type: str = 'interval',
                interval_minutes: Optional[int] = None,
                time_str: Optional[str] = None,
                job_name: Optional[str] = None):
        """
        Adiciona um job ao scheduler
        
        Args:
            func: Função a ser executada
            schedule_type: 'interval' (a cada X minutos) ou 'time' (horário específico)
            interval_minutes: Intervalo em minutos (para schedule_type='interval')
            time_str: Horário no formato "HH:MM" (para schedule_type='time')
            job_name: Nome do job para identificação
        """
        if job_name is None:
            job_name = func.__name__
        
        # Wrapper para logar execução
        def wrapped_func():
            start_time = time.time()
            try:
                func()
                duration = time.time() - start_time
                self._log_execution(job_name, 'success', duration)
            except Exception as e:
                duration = time.time() - start_time
                self._log_execution(job_name, 'error', duration, str(e))
                print(f"Erro ao executar job {job_name}: {e}")
        
        if schedule_type == 'interval' and interval_minutes:
            job = schedule.every(interval_minutes).minutes.do(wrapped_func)
        elif schedule_type == 'time' and time_str:
            job = schedule.every().day.at(time_str).do(wrapped_func)
        else:
            raise ValueError("Configuração de agendamento inválida")
        
        self.jobs.append({
            'job': job,
            'name': job_name,
            'func': func,
            'schedule_type': schedule_type,
            'config': {
                'interval_minutes': interval_minutes,
                'time_str': time_str
            }
        })
        
        print(f"✅ Job '{job_name}' agendado com sucesso")
    
    def remove_job(self, job_name: str):
        """Remove um job pelo nome"""
        for job_info in self.jobs:
            if job_info['name'] == job_name:
                schedule.cancel_job(job_info['job'])
                self.jobs.remove(job_info)
                print(f"🗑️ Job '{job_name}' removido")
                return True
        return False
    
    def start(self):
        """Inicia o scheduler em background"""
        if self.is_running:
            print("⚠️ Scheduler já está rodando")
            return
        
        self.is_running = True
        
        def run_scheduler():
            print("🚀 Scheduler iniciado")
            while self.is_running:
                schedule.run_pending()
                time.sleep(1)
            print("🛑 Scheduler parado")
        
        self.thread = threading.Thread(target=run_scheduler, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Para o scheduler"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=5)
        print("🛑 Scheduler parado")
    
    def get_job_status(self) -> List[Dict]:
        """Retorna status de todos os jobs"""
        status = []
        
        for job_info in self.jobs:
            last_run = None
            next_run = job_info['job'].next_run
            
            # Busca última execução no log
            job_logs = [
                log for log in self.execution_log 
                if log['job_name'] == job_info['name']
            ]
            
            if job_logs:
                last_log = job_logs[-1]
                last_run = last_log['timestamp']
                last_status = last_log['status']
            else:
                last_status = 'never_run'
            
            status.append({
                'name': job_info['name'],
                'schedule_type': job_info['schedule_type'],
                'config': job_info['config'],
                'last_run': last_run,
                'last_status': last_status,
                'next_run': next_run.isoformat() if next_run else None
            })
        
        return status
    
    def get_execution_history(self, job_name: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """
        Retorna histórico de execuções
        
        Args:
            job_name: Nome do job (None para todos)
            limit: Número máximo de registros
        """
        if job_name:
            history = [
                log for log in self.execution_log 
                if log['job_name'] == job_name
            ]
        else:
            history = self.execution_log
        
        return history[-limit:]
    
    def clear_old_logs(self, days: int = 30):
        """Remove logs antigos"""
        cutoff = datetime.now() - timedelta(days=days)
        
        self.execution_log = [
            log for log in self.execution_log
            if datetime.fromisoformat(log['timestamp']) > cutoff
        ]
        
        self._save_log()
        print(f"🗑️ Logs anteriores a {days} dias removidos")
