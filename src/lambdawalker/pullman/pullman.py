import asyncio
import hashlib
import inspect
import json
import multiprocessing
import multiprocessing.connection
import os
import pathlib
import queue
import threading
import time
import traceback
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, Type

# Attempt to import psutil for resource monitoring
try:
    import psutil
except ImportError:
    psutil = None

# Rich imports for the UI
from rich.live import Live
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn, TimeRemainingColumn
from rich.panel import Panel
from rich.console import Group, RenderableType
from rich.columns import Columns

# --- Internal Protocol Constants ---
MSG_READY = "READY"
MSG_ASSIGN = "ASSIGN"
MSG_LOG = "LOG"
MSG_RESULT = "RESULT"
MSG_PROGRESS = "PROGRESS"
MSG_SHUTDOWN = "SHUTDOWN"


class TaskExecutionError(Exception):
    """Custom exception for library-level errors."""
    pass


class BaseWorker:
    """
    Base class for Parallel Task Workers.
    Users should inherit from this and override the 'work' method.
    Optional: Override 'setup' for initialization and 'teardown' for cleanup.
    """

    def __init__(self, pipe: multiprocessing.connection.Connection, worker_id: int, blackboard: Dict[str, Any]):
        self.pipe = pipe
        self.worker_id = worker_id
        self.blackboard = blackboard  # Shared memory access
        self.current_task_id = None

    async def setup(self):
        """
        Optional: Override this method to initialize heavy resources.
        Called once per worker process startup.
        Supports both synchronous and 'async def' implementations.
        """
        pass

    async def teardown(self):
        """
        Optional: Override this method to clean up resources (DB connections, etc).
        Called once per worker process just before exit.
        Supports both synchronous and 'async def' implementations.
        """
        pass

    def log(self, message: str):
        """Sends a log message to the Coordinator to be written to the task log file."""
        if self.current_task_id is not None:
            msg = {
                "type": MSG_LOG,
                "task_id": self.current_task_id,
                "msg": message
            }
            try:
                self.pipe.send(json.dumps(msg))
            except (BrokenPipeError, ConnectionResetError):
                pass

    def report_progress(self, percent: float):
        """
        Reports the progress of the current task (0.0 to 1.0).
        This will be reflected in the Orchestrator's UI.
        """
        if self.current_task_id is not None:
            msg = {
                "type": MSG_PROGRESS,
                "task_id": self.current_task_id,
                "worker_id": self.worker_id,
                "value": max(0.0, min(1.0, percent))
            }
            try:
                self.pipe.send(json.dumps(msg))
            except (BrokenPipeError, ConnectionResetError):
                pass

    def work(self, payload: Dict[str, Any]) -> Any:
        """
        Override this method with custom logic.
        Return a JSON-serializable value to store it in the results.
        Supports both synchronous and 'async def' implementations.
        """
        raise NotImplementedError("Subclasses must implement the 'work' method.")

    def _run_loop(self):
        """Internal execution loop handling the lifecycle and IPC protocol."""
        try:
            # 1. Run Setup (detect async)
            if inspect.iscoroutinefunction(self.setup):
                asyncio.run(self.setup())
            else:
                self.setup()

            # 2. Main Pull Loop
            while True:
                self.pipe.send(json.dumps({"type": MSG_READY, "worker_id": self.worker_id}))
                try:
                    raw_msg = self.pipe.recv()
                except (EOFError, ConnectionResetError):
                    break

                msg = json.loads(raw_msg)
                if msg["type"] == MSG_SHUTDOWN:
                    break

                if msg["type"] == MSG_ASSIGN:
                    task = msg["task"]
                    self.current_task_id = task["id"]
                    payload = task.get("payload", {})

                    result_data = None
                    try:
                        # 3. Run Work (detect async)
                        if inspect.iscoroutinefunction(self.work):
                            result_data = asyncio.run(self.work(payload))
                        else:
                            result_data = self.work(payload)
                        status = "PASS"
                    except Exception:
                        status = "FAIL"
                        error_trace = traceback.format_exc()
                        self.log(f"Exception in task {self.current_task_id}:\n{error_trace}")

                    try:
                        self.pipe.send(json.dumps({
                            "type": MSG_RESULT,
                            "task_id": self.current_task_id,
                            "status": status,
                            "data": result_data
                        }))
                    except (BrokenPipeError, ConnectionResetError):
                        break

                    self.current_task_id = None
        except Exception as e:
            print(f"Worker {self.worker_id} fatal error: {e}")
        finally:
            # 4. Run Teardown (detect async)
            try:
                if inspect.iscoroutinefunction(self.teardown):
                    asyncio.run(self.teardown())
                else:
                    self.teardown()
            except Exception as e:
                print(f"Worker {self.worker_id} teardown error: {e}")


def _worker_process_launcher(worker_class: Type[BaseWorker], pipe: multiprocessing.connection.Connection, worker_id: int, blackboard: Dict[str, Any]):
    """Helper to instantiate and run the user-defined worker class in a sub-process."""
    worker_instance = worker_class(pipe, worker_id, blackboard)
    worker_instance._run_loop()


class StorageManager:
    """Handles persistence in the .pullman directory grouped by session_id."""

    def __init__(self, session_id: str, base_dir: str = ".pullman"):
        self.session_id = session_id
        self.root_path = pathlib.Path(base_dir)
        self.session_path = self.root_path / session_id

        self.root_path.mkdir(exist_ok=True)
        self.session_path.mkdir(exist_ok=True)

        self.tasks_file = self.session_path / "tasks.json"
        self.results_file = self.session_path / "results.json"
        self.hash_file = self.session_path / "workload.hash"
        self.lock = threading.Lock()

    def calculate_workload_hash(self, tasks: List[Dict]) -> str:
        """Generates a stable SHA-256 hash of the task list."""
        task_str = json.dumps(tasks, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(task_str.encode('utf-8')).hexdigest()

    def verify_workload(self, tasks: List[Dict]) -> bool:
        if not self.hash_file.exists():
            return True

        current_hash = self.calculate_workload_hash(tasks)
        with open(self.hash_file, "r") as f:
            stored_hash = f.read().strip()

        return current_hash == stored_hash

    def save_workload_metadata(self, tasks: List[Dict]):
        workload_hash = self.calculate_workload_hash(tasks)
        with self.lock:
            with open(self.tasks_file, "w") as f:
                json.dump(tasks, f, indent=4)
            with open(self.hash_file, "w") as f:
                f.write(workload_hash)

    def save_results(self, results: Dict[str, Any]):
        """Updates the dynamic results state safely."""
        results_snapshot = dict(results)

        with self.lock:
            data = {
                "last_updated": datetime.now().isoformat(),
                "results": results_snapshot
            }
            with open(self.results_file, "w") as f:
                json.dump(data, f, indent=4)

    def load_state(self) -> Optional[Dict[str, Any]]:
        if not self.tasks_file.exists():
            return None

        try:
            with open(self.tasks_file, "r") as f:
                tasks = json.load(f)

            results = {}
            if self.results_file.exists():
                with open(self.results_file, "r") as f:
                    results_data = json.load(f)
                    results = results_data.get("results", {})

            return {"tasks": tasks, "results": results}
        except Exception:
            return None

    def clear_session(self):
        with self.lock:
            for file in [self.results_file, self.tasks_file, self.hash_file]:
                if file.exists():
                    file.unlink()
            try:
                self.session_path.rmdir()
            except OSError:
                pass


class DashboardUI:
    """Handles the Rich-based console UI rendering."""

    def __init__(self, total_tasks: int, max_workers: int, session_id: str):
        self.total_tasks = total_tasks
        self.max_workers = max_workers
        self.session_id = session_id
        self.aborted = False
        self.worker_status = {
            i: {
                "status": "Starting",
                "task": "-",
                "start_time": None,
                "speed": "0.00s",
                "progress": 0.0,
                "cpu": 0.0,
                "ram": 0.0,
                "logs": [],  # Buffer for the latest log messages
                "success": 0,
                "failed": 0,
                "durations": []
            } for i in range(max_workers)
        }

        self.progress = Progress(
            TextColumn("[bold blue]{task.description}"),
            BarColumn(bar_width=None),
            "[progress.percentage]{task.percentage:>3.0f}%",
            "•",
            TextColumn("[green]{task.completed}/{task.total}"),
            "•",
            TimeElapsedColumn(),
            "•",
            TimeRemainingColumn(),
        )
        self.task_id = self.progress.add_task("Total Progress", total=total_tasks)

    def set_aborted(self):
        self.aborted = True

    def update_worker_start(self, worker_id: int, status: str, task_id: str = "-"):
        worker = self.worker_status[worker_id]
        worker["status"] = status
        worker["task"] = task_id
        worker["progress"] = 0.0
        worker["logs"] = []  # Clear logs for the new task
        if status == "Working":
            worker["start_time"] = time.time()

    def update_worker_progress(self, worker_id: int, value: float):
        worker = self.worker_status[worker_id]
        worker["progress"] = value

    def update_worker_log(self, worker_id: int, message: str):
        """Appends a log message to the worker's card buffer."""
        worker = self.worker_status[worker_id]
        # Keep only the last 2 lines for UI space efficiency
        worker["logs"].append(message.strip())
        if len(worker["logs"]) > 2:
            worker["logs"].pop(0)

    def update_worker_resources(self, worker_id: int, cpu: float, ram_mb: float):
        worker = self.worker_status[worker_id]
        worker["cpu"] = cpu
        worker["ram"] = ram_mb

    def update_worker_result(self, worker_id: int, status: str, result_status: Optional[str] = None):
        worker = self.worker_status[worker_id]
        worker["status"] = status
        worker["task"] = "-"
        worker["progress"] = 0.0
        worker["cpu"] = 0.0
        worker["ram"] = 0.0

        if worker["start_time"]:
            duration = time.time() - worker["start_time"]
            worker["speed"] = f"{duration:.2f}s"
            worker["durations"].append(duration)
            worker["start_time"] = None

        if result_status == "PASS":
            worker["success"] += 1
            worker["logs"] = ["[green]Task Passed[/]"]
        elif result_status in ["FAIL", "CRASHED", "TIMED_OUT"]:
            worker["failed"] += 1
            worker["logs"] = [f"[red]Task {result_status}[/]"]

    def increment_progress(self, amount=1):
        self.progress.advance(self.task_id, amount)

    def _get_trimmed_avg(self, durations: List[float]) -> str:
        if not durations: return "0.00s"
        if len(durations) < 3: return f"{sum(durations) / len(durations):.2f}s"
        sorted_data = sorted(durations)
        trim_count = max(1, int(len(durations) * 0.1))
        trimmed = sorted_data[trim_count:-trim_count]
        avg = sum(trimmed) / len(trimmed) if trimmed else sum(durations) / len(durations)
        return f"{avg:.2f}s"

    def _make_worker_card(self, worker_id: int) -> RenderableType:
        info = self.worker_status[worker_id]
        status = info["status"]
        task = info["task"]
        speed = info["speed"]
        success = info["success"]
        failed = info["failed"]
        task_progress = info["progress"]
        cpu = info["cpu"]
        ram = info["ram"]
        logs = info["logs"]
        total = success + failed
        avg_speed = self._get_trimmed_avg(info["durations"])

        status_style = {"Ready": "green", "Working": "yellow", "Crashed": "red", "Finished": "blue", "Starting": "cyan"}.get(status, "white")
        if self.aborted and status != "Finished":
            status_style = "red"
            status = "Aborted"

        stats_line = f"[green]{success}[/] / [red]{failed}[/] / [white]{total}[/]"

        # Intra-task progress bar
        if status == "Working":
            bar_width = 18
            filled = int(task_progress * bar_width)
            bar = "━" * filled + "╌" * (bar_width - filled)
            progress_line = f"[{status_style}]{bar}[/] {int(task_progress * 100)}%"
            resource_line = f"CPU: [blue]{cpu:>4.1f}%[/] | RAM: [yellow]{ram:>5.1f}MB[/]"
        else:
            progress_line = "[dim]Idle[/]"
            resource_line = "[dim]CPU: 0.0% | RAM: 0.0MB[/]"

        # Logs Tailing
        log_content = ""
        if logs:
            log_lines = []
            for line in logs:
                # Truncate long log lines to fit card
                truncated = (line[:28] + "..") if len(line) > 28 else line
                log_lines.append(f"[dim]› {truncated}[/]")
            log_content = "\n".join(log_lines)
        else:
            log_content = "[dim italic]Waiting for logs...[/]"

        content = (
            f"[bold cyan]Worker {worker_id}[/]\n"
            f"Status: [{status_style}]{status}[/]\n"
            f"Active: [magenta]{task}[/]\n"
            f"Resources: {resource_line}\n"
            f"Progress: {progress_line}\n"
            f"Logs:\n{log_content}\n"
            f"Stats: {stats_line}\n"
            f"Last: [green]{speed}[/] | Avg: [bold white]{avg_speed}[/]"
        )
        return Panel(content, width=34, border_style=status_style)

    def __rich__(self) -> Group:
        cards = [self._make_worker_card(i) for i in range(self.max_workers)]
        worker_grid = Columns(cards, equal=True, expand=False, padding=(1, 2))

        title_style = "red" if self.aborted else "blue"
        session_prefix = "[bold red]ABORTED - [/]" if self.aborted else ""

        return Group(
            Panel(self.progress, title=f"{session_prefix}Session: {self.session_id}", border_style=title_style),
            Panel(worker_grid, title="Worker Status Grid", border_style="white")
        )


class Orchestrator:
    def __init__(
            self,
            tasks: List[Dict[str, Any]],
            worker_class: Type[BaseWorker],
            max_workers: int = 1,
            worker_scale: Optional[float] = None,
            log_path: str = "./logs",
            session_id: str = "default_session",
            retries: int = 0,
            show_ui: bool = True,
            resume: bool = True,
            force: bool = False,
            blackboard: Optional[Dict[str, Any]] = None  # Shared Blackboard parameter
    ):
        self.storage = StorageManager(session_id)
        self.session_id = session_id
        self.tasks_data = {t["id"]: t for t in tasks}
        self.worker_class = worker_class
        self.log_path = log_path
        self.retries = retries
        self.show_ui = show_ui
        self.initial_blackboard = blackboard
        self.shared_blackboard = None

        self.max_workers = self._calculate_concurrency(max_workers, worker_scale)
        self.results = {}
        self.results_lock = threading.Lock()
        self.retry_counts = {t["id"]: 0 for t in tasks}

        # Resume/Force Logic
        active_tasks = tasks
        if force:
            self.storage.clear_session()
            self.storage = StorageManager(session_id)
        elif resume:
            if not self.storage.verify_workload(tasks):
                raise TaskExecutionError(f"Session '{session_id}' workload changed. Use 'force=True' to reset.")

            saved_state = self.storage.load_state()
            if saved_state:
                with self.results_lock:
                    self.results = saved_state.get("results", {})
                active_tasks = [t for t in tasks if self._get_status(t["id"]) != "PASS"]

        self.storage.save_workload_metadata(list(self.tasks_data.values()))

        # Priority Queue Support
        self.pending_tasks = queue.PriorityQueue()
        for t in active_tasks:
            priority = t.get("priority", 100)
            self.pending_tasks.put((priority, t["id"]))

        self.workers: Dict[int, multiprocessing.Process] = {}
        self.monitor_threads: List[threading.Thread] = []
        self.stop_event = threading.Event()
        self.abort_triggered = False

        if self.show_ui:
            self.ui = DashboardUI(len(self.tasks_data), self.max_workers, session_id)
            if self.results and not force:
                with self.results_lock:
                    completed_count = sum(1 for v in self.results.values() if self._get_status_from_val(v) == "PASS")
                self.ui.increment_progress(completed_count)

        self._validate_config()

    def _get_status(self, task_id: str) -> Optional[str]:
        val = self.results.get(task_id)
        return self._get_status_from_val(val)

    def _get_status_from_val(self, val: Any) -> Optional[str]:
        if isinstance(val, dict):
            return val.get("status")
        return val

    # --- Hooks ---
    def on_task_start(self, task_id: str, worker_id: int):
        pass

    def on_task_success(self, task_id: str, data: Any):
        pass

    def on_task_error(self, task_id: str, status: str):
        pass

    def reducer(self, results: Dict[str, Any]) -> Any:
        """Hook to aggregate results after all tasks are finished."""
        return results

    def _calculate_concurrency(self, base_max: int, scale: Optional[float]) -> int:
        final_count = base_max
        if scale is not None:
            cpu_count = multiprocessing.cpu_count()
            scaled_count = max(1, int(cpu_count * scale))
            final_count = max(base_max, scaled_count)
        return final_count

    def _validate_config(self):
        if not os.path.exists(self.log_path): os.makedirs(self.log_path)
        if self.max_workers < 1: raise ValueError("max_workers must be at least 1")
        if not issubclass(self.worker_class, BaseWorker): raise TypeError("worker_class must inherit from BaseWorker")

    def _write_log(self, task_id: Union[str, int], message: str):
        filename = os.path.join(self.log_path, f"{task_id}.log")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(filename, "a") as f:
            f.write(f"[{timestamp}] {message}\n")

    def _should_retry(self, task_id: Union[str, int], reason: str) -> bool:
        if self.retry_counts[task_id] < self.retries:
            self.retry_counts[task_id] += 1
            self._write_log(task_id, f"RETRYING: {reason}. Attempt {self.retry_counts[task_id]}/{self.retries}")
            priority = self.tasks_data[task_id].get("priority", 100)
            self.pending_tasks.put((priority, task_id))
            return True
        return False

    def _handle_critical_failure(self, task_id: str, status: str):
        if self.abort_triggered: return
        self.abort_triggered = True
        self._write_log("SYSTEM", f"CRITICAL FAILURE: Task '{task_id}' {status}. Aborting session.")
        try:
            while True: self.pending_tasks.get_nowait()
        except queue.Empty:
            pass
        if self.show_ui: self.ui.set_aborted()
        self.stop_event.set()

    def _monitor_worker(self, worker_id: int, pipe: multiprocessing.connection.Connection):
        current_task_id = None
        task_start_time = None
        timeout = None
        ps_process = None
        last_resource_update = 0

        try:
            while not self.stop_event.is_set():
                if psutil and time.time() - last_resource_update > 1.0:
                    try:
                        worker_proc = self.workers.get(worker_id)
                        if worker_proc and worker_proc.is_alive():
                            if ps_process is None or ps_process.pid != worker_proc.pid:
                                ps_process = psutil.Process(worker_proc.pid)
                            cpu = ps_process.cpu_percent()
                            ram_mb = ps_process.memory_info().rss / (1024 * 1024)
                            if self.show_ui: self.ui.update_worker_resources(worker_id, cpu, ram_mb)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        ps_process = None
                    last_resource_update = time.time()

                if pipe.poll(0.1):
                    try:
                        raw_msg = pipe.recv()
                    except (EOFError, ConnectionResetError):
                        self._handle_crash(worker_id, current_task_id)
                        return

                    msg = json.loads(raw_msg)
                    msg_type = msg.get("type")

                    if msg_type == MSG_READY:
                        if self.show_ui: self.ui.update_worker_result(worker_id, "Ready")
                        if self.stop_event.is_set():
                            try:
                                pipe.send(json.dumps({"type": MSG_SHUTDOWN}))
                            except:
                                pass
                            return
                        try:
                            _, tid = self.pending_tasks.get_nowait()
                            task = self.tasks_data[tid]
                            current_task_id = tid
                            timeout = task.get("timeout")
                            task_start_time = time.time()
                            self.on_task_start(tid, worker_id)
                            if self.show_ui: self.ui.update_worker_start(worker_id, "Working", current_task_id)
                            pipe.send(json.dumps({"type": MSG_ASSIGN, "task": task}))
                        except queue.Empty:
                            try:
                                pipe.send(json.dumps({"type": MSG_SHUTDOWN}))
                            except (BrokenPipeError, ConnectionResetError):
                                pass
                            if self.show_ui: self.ui.update_worker_result(worker_id, "Finished")
                            return

                    elif msg_type == MSG_LOG:
                        self._write_log(msg["task_id"], msg["msg"])
                        if self.show_ui: self.ui.update_worker_log(worker_id, msg["msg"])

                    elif msg_type == MSG_PROGRESS:
                        if self.show_ui: self.ui.update_worker_progress(msg["worker_id"], msg["value"])

                    elif msg_type == MSG_RESULT:
                        tid = msg["task_id"]
                        status = msg["status"]
                        data = msg.get("data")

                        if status == "FAIL" and self._should_retry(tid, "execution error"):
                            if self.show_ui: self.ui.update_worker_result(worker_id, "Ready", "FAIL")
                            current_task_id = None
                            continue

                        with self.results_lock:
                            self.results[tid] = {"status": status, "data": data}
                            self.storage.save_results(self.results)

                        if status == "PASS":
                            self.on_task_success(tid, data)
                        else:
                            self.on_task_error(tid, status)
                            if self.tasks_data[tid].get("critical", False):
                                self._handle_critical_failure(tid, status)
                                return

                        self._write_log(tid, f"Task finished: {status}")
                        if self.show_ui:
                            self.ui.increment_progress()
                            self.ui.update_worker_result(worker_id, "Ready", status)
                        current_task_id = None
                        task_start_time = None

                if current_task_id and timeout and task_start_time:
                    if (time.time() - task_start_time) > timeout:
                        self._handle_timeout(worker_id, current_task_id)
                        return

        except Exception as e:
            error_message = traceback.format_exc()
            self._write_log("SYSTEM", f"Monitor Thread {worker_id} Error:\n{error_message}")

    def _handle_crash(self, worker_id: int, current_task_id: Optional[Union[str, int]]):
        if self.show_ui: self.ui.update_worker_result(worker_id, "Crashed", "CRASHED")
        if current_task_id:
            if not self._should_retry(current_task_id, "process crash"):
                with self.results_lock:
                    self.results[current_task_id] = {"status": "CRASHED", "data": None}
                    self.storage.save_results(self.results)
                self.on_task_error(current_task_id, "CRASHED")
                self._write_log(current_task_id, "ERROR: Worker process terminated unexpectedly.")
                if self.tasks_data[current_task_id].get("critical", False):
                    self._handle_critical_failure(current_task_id, "CRASHED")
                    return
                if self.show_ui: self.ui.increment_progress()
        if not self.stop_event.is_set(): self._spawn_worker(worker_id)

    def _handle_timeout(self, worker_id: int, task_id: Union[str, int]):
        self._write_log(task_id, f"TIMEOUT: Terminating worker {worker_id}.")
        process = self.workers.get(worker_id)
        if process:
            process.terminate()
            process.join()
        if not self._should_retry(task_id, "timeout"):
            with self.results_lock:
                self.results[task_id] = {"status": "TIMED_OUT", "data": None}
                self.storage.save_results(self.results)
            self.on_task_error(task_id, "TIMED_OUT")
            if self.tasks_data[task_id].get("critical", False):
                self._handle_critical_failure(task_id, "TIMED_OUT")
                return
            if self.show_ui:
                self.ui.increment_progress()
                self.ui.update_worker_result(worker_id, "Ready", "TIMED_OUT")
        if not self.stop_event.is_set(): self._spawn_worker(worker_id)

    def _spawn_worker(self, worker_id: int):
        parent_conn, child_conn = multiprocessing.Pipe(duplex=True)
        process = multiprocessing.Process(
            target=_worker_process_launcher,
            args=(self.worker_class, child_conn, worker_id, self.shared_blackboard),
            daemon=True
        )
        self.workers[worker_id] = process
        process.start()
        thread = threading.Thread(target=self._monitor_worker, args=(worker_id, parent_conn), daemon=True)
        self.monitor_threads.append(thread)
        thread.start()

    def run(self):
        with multiprocessing.Manager() as manager:
            self.shared_blackboard = manager.dict(self.initial_blackboard or {})

            if self.show_ui:
                with Live(self.ui, refresh_per_second=10, screen=False):
                    self._execute()
            else:
                self._execute()

            with self.results_lock:
                all_passed = all(self._get_status_from_val(v) == "PASS" for v in self.results.values())

            if all_passed and not self.abort_triggered:
                self.storage.clear_session()

            return self.reducer(self.results)

    def _execute(self):
        for i in range(self.max_workers): self._spawn_worker(i)
        while any(t.is_alive() for t in self.monitor_threads):
            time.sleep(0.1)
            if self.stop_event.is_set() and self.abort_triggered: break
        self.stop_event.set()
        for p in self.workers.values():
            if p.is_alive():
                if self.abort_triggered: p.terminate()
                p.join(timeout=1)





