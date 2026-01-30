### Lambdawaker Executor

A reusable package for running multi-process tasks with real-time progress reporting and status monitoring via a robust
signaling protocol.

#### Features

- **Decoupled Architecture**: Separates task execution logic from UI reporting.
- **Signaling Protocol**: Workers communicate progress, status, and messages via standard output.
- **Subprocess Management**: Handles spawning, monitoring, and retrying worker processes.
- **Rich Terminal UI**: Provides a detailed, responsive dashboard using the `rich` library.
- **Graceful Termination**: Supports clean shutdown of all worker processes.

#### Architecture

The package is organized into four main components:

1. **`models.py`**: Contains core data structures:
    - `TaskStatus`: Enum for task states (`PENDING`, `RUNNING`, `SUCCESS`, `FAILED`, `CRASHED`, `RETRYING`, `FINISHED`).
    - `WorkerState`: Tracks the current state, progress, and metadata for an individual worker.
    - `TaskConfig`: Global configuration for the execution run (total items, number of workers, retries, etc.).

2. **`engine.py`**: The execution core:
    - `ProtocolHandler`: Parses worker output lines following the signaling protocol.
    - `SubprocessExecutor`: Manages a pool of subprocesses, maps work ranges to workers, and handles execution
      lifecycle.

3. **`reporter.py`**: The visualization layer:
    - `RichReporter`: A `rich`-based implementation that displays a global progress bar and a grid of worker panels.

4. **`mock_task.py`**: A utility script for testing and demonstrating the protocol.

#### Signaling Protocol

Workers communicate with the executor by printing specific prefixes to `stdout`. The `ProtocolHandler` recognizes:

- `PROGRESS: <int>`: Updates the current completion count for the worker.
- `STATUS: <status_name>`: Changes the worker's status (e.g., `STATUS: RUNNING`, `STATUS: SUCCESS`).
- `MESSAGE: <string>`: Displays an arbitrary message in the worker's UI panel.

**Example Worker Output:**

```text
STATUS: RUNNING
MESSAGE: Initializing resources...
PROGRESS: 10
MESSAGE: Processing batch 1...
PROGRESS: 20
STATUS: SUCCESS
```

#### Usage Example

To use the executor, define a function that generates the command for each worker and run the `SubprocessExecutor`.

```python
import sys
from lambdawaker.executor.models import TaskConfig
from lambdawaker.executor.engine import SubprocessExecutor
from lambdawaker.executor.reporter import RichReporter

# 1. Configuration
config = TaskConfig(
    total_items=1000,
    num_workers=4,
    max_retries=3,
    grid_cols=2
)

# 2. Command generator
def get_command(state):
    # Use state.extra_data to get work range
    start = state.extra_data['start_index']
    end = state.extra_data['end_index']
    return [sys.executable, "my_worker_script.py", "--start", str(start), "--end", str(end)]

# 3. Execution
executor = SubprocessExecutor(config, get_command)
reporter = RichReporter(title="My Parallel Task")

executor.run(reporter)
```

#### Demo

You can see a live demonstration of the executor and reporter by running:

```bash
python src/lambdawaker/executor/demo.py
```
