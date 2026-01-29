#!/usr/bin/env python3
import os
import sys
from pathlib import Path

from lambdawaker.executor.engine import SubprocessExecutor
from lambdawaker.executor.models import TaskConfig
from lambdawaker.executor.reporter import RichReporter

WORKER_SCRIPT = Path(__file__).parent / "render_in_series.py"


def run_dispatcher(dataset_size, config):
    limit = config.limit if config.limit is not None else sys.maxsize

    total = min(dataset_size, limit)

    if total == sys.maxsize:
        raise RuntimeError("Dataset size could not be determined and no limit was provided.")

    cpu_count = os.cpu_count() or 1
    worker_count = max(4, round(cpu_count * (config.worker_load_percent / 100.0)))

    taskConfig = TaskConfig(
        total_items=total,
        num_workers=worker_count,
        max_retries=config.max_retries,
        refresh_hz=config.refresh_hz,
        grid_cols=config.grid_cols
    )

    def get_command(state):
        start = state.extra_data['start_index']
        end = state.extra_data['end_index']
        cmd = [
            sys.executable, str(WORKER_SCRIPT),
            "--start", str(start),
            "--end", str(end),
            "--base-url", config.base_url,
            "--outdir", config.outdir,
        ]
        if config.headless:
            cmd.append("--headless")
        else:
            cmd.append("--no-headless")
        return cmd

    executor = SubprocessExecutor(taskConfig, get_command)
    reporter = RichReporter(title=f"Parallel Rendering ({worker_count} Workers)")

    executor.run(reporter)
