"""
detection/services/trainer.py
=============================
Background trainer service for TruthLens ML Models.
Executes model training asynchronously in a dedicated worker thread,
captures real-time terminal stdout/stderr stream, computes elapsed time,
and exposes live polling state for frontend console terminals.
"""

import os
import sys
import time
import subprocess
import threading
import logging
from datetime import datetime
from django.conf import settings

logger = logging.getLogger(__name__)


class ModelTrainerState:
    _lock = threading.Lock()
    _instance = None

    def __init__(self):
        self.status = 'idle'  # 'idle' | 'running' | 'completed' | 'failed'
        self.start_time = None
        self.end_time = None
        self.elapsed_seconds = 0.0
        self.logs = []  # list of { time, text, level }
        self.progress = 0  # 0 to 100
        self.current_step = 'Ready'
        self.metrics = {
            'accuracy': None,
            'f1_score': None,
            'train_samples': 10240,
            'test_samples': 2551,
            'duration_seconds': 0.0,
        }
        self.worker_thread = None
        self.process = None

    @classmethod
    def get_instance(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def _append_log(self, text, level='info'):
        now_str = datetime.now().strftime('%H:%M:%S')
        self.logs.append({
            'time': now_str,
            'text': text,
            'level': level
        })

    def start_training(self):
        with self._lock:
            if self.status == 'running':
                return False, "Training is already in progress."

            self.status = 'running'
            self.start_time = time.time()
            self.end_time = None
            self.elapsed_seconds = 0.0
            self.progress = 5
            self.current_step = 'Initializing Training Pipeline...'
            self.logs = []
            self.metrics = {
                'accuracy': None,
                'f1_score': None,
                'train_samples': 10240,
                'test_samples': 2551,
                'duration_seconds': 0.0,
            }

            self._append_log("🚀 [TruthLens ML Engine] Initializing training pipeline...", "info")
            self._append_log("📂 Environment: Python 3 (venv) | Base: " + str(settings.BASE_DIR), "info")

            self.worker_thread = threading.Thread(target=self._run_training_worker, daemon=True)
            self.worker_thread.start()
            return True, "Training process launched successfully."

    def _run_training_worker(self):
        base_dir = str(settings.BASE_DIR)
        train_script = os.path.join(base_dir, 'train_model.py')
        venv_python = os.path.join(base_dir, '.venv', 'bin', 'python')
        if not os.path.exists(venv_python):
            venv_python = sys.executable

        cmd = [venv_python, '-u', train_script]
        self._append_log(f"⚡ Executing command: {' '.join(cmd)}", "info")

        try:
            self.process = subprocess.Popen(
                cmd,
                cwd=base_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            for line in self.process.stdout:
                clean_line = line.rstrip()
                if not clean_line:
                    continue

                # Parse progress markers from train_model.py output
                level = 'info'
                if '[1/5]' in clean_line:
                    self.progress = 20
                    self.current_step = 'Loading Dataset (train.csv & test.csv)...'
                elif '[2/5]' in clean_line:
                    self.progress = 40
                    self.current_step = 'Building TF-IDF N-Gram Vectorizer Pipeline...'
                elif '[3/5]' in clean_line:
                    self.progress = 60
                    self.current_step = 'Training Multi-Model Classifiers & Optimizing Weights...'
                elif 'Training complete!' in clean_line:
                    self.progress = 75
                elif '[4/5]' in clean_line:
                    self.progress = 80
                    self.current_step = 'Evaluating Precision, Recall & F1 on Test Set...'
                elif 'Accuracy :' in clean_line:
                    level = 'success'
                    try:
                        acc_val = float(clean_line.split(':')[1].replace('%', '').strip())
                        self.metrics['accuracy'] = acc_val
                    except Exception:
                        pass
                elif 'F1 Score :' in clean_line:
                    level = 'success'
                    try:
                        f1_val = float(clean_line.split(':')[1].replace('%', '').strip())
                        self.metrics['f1_score'] = f1_val
                    except Exception:
                        pass
                elif '[5/5]' in clean_line:
                    self.progress = 90
                    self.current_step = 'Serializing Model to final_model.sav...'
                elif '[DONE]' in clean_line:
                    self.progress = 100
                    self.current_step = 'Training Successfully Completed!'
                    level = 'success'

                self._append_log(clean_line, level=level)

            self.process.wait()
            rc = self.process.returncode
            self.end_time = time.time()
            self.elapsed_seconds = round(self.end_time - self.start_time, 2)
            self.metrics['duration_seconds'] = self.elapsed_seconds

            if rc == 0:
                self.status = 'completed'
                self.progress = 100
                self.current_step = f"Completed in {self.elapsed_seconds}s"
                self._append_log(f"✅ Training completed successfully in {self.elapsed_seconds}s. Model artifact ready.", "success")
                # Reload active models in detection service if loaded
                try:
                    from detection.services.detector import _LOADED_MODELS
                    _LOADED_MODELS['initialized'] = False
                except Exception:
                    pass
            else:
                self.status = 'failed'
                self.current_step = f"Failed with exit code {rc}"
                self._append_log(f"❌ Training process exited with code {rc}", "error")

        except Exception as e:
            logger.error(f"Error in training worker: {e}", exc_info=True)
            self.status = 'failed'
            self.end_time = time.time()
            self.elapsed_seconds = round(self.end_time - (self.start_time or time.time()), 2)
            self.current_step = f"Error: {str(e)}"
            self._append_log(f"💥 Exception during training execution: {str(e)}", "error")

    def get_status_payload(self, since_index=0):
        with self._lock:
            current_elapsed = self.elapsed_seconds
            if self.status == 'running' and self.start_time:
                current_elapsed = round(time.time() - self.start_time, 1)

            logs_slice = self.logs[since_index:] if since_index < len(self.logs) else []

            return {
                'status': self.status,
                'is_running': (self.status == 'running'),
                'progress': self.progress,
                'current_step': self.current_step,
                'start_time': self.start_time,
                'elapsed_seconds': current_elapsed,
                'metrics': self.metrics,
                'total_log_count': len(self.logs),
                'logs': logs_slice,
            }
