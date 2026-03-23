# **Pullman**

**Pullman** is a production-grade, Python-based parallel task execution library designed for reliability, visibility, and performance. It utilizes a pull-based architecture where worker processes request work from a central Orchestrator, ensuring optimal load balancing across your CPU cores.

## **Key Features**

* 🚀 **Pull-based Concurrency**: Maximizes throughput by having workers request tasks as they become free.  
* 📊 **Real-time Dashboard**: A beautiful rich-based UI showing worker cards, progress bars, processing speeds, and log tails.  
* 💾 **Session Persistence**: Interrupted runs can be resumed exactly where they left off in the .pullman directory.  
* 🛡️ **Workload Integrity**: SHA-256 hashing ensures session data is only resumed if the task list hasn't changed.  
* 🧠 **Shared Memory (Blackboard)**: Efficiently share heavy assets across processes using a shared dictionary.  
* 🩺 **Resource Monitoring**: Live CPU and RAM tracking per worker process (via psutil).  
* ⚠️ **Resilience**: Integrated retry logic, task timeouts, and "Critical Task" abort triggers.  
* 🛠️ **Advanced Hooks**: Custom reducers for result aggregation and event hooks for workflow management.

## **Installation**

Ensure you have the required dependencies:

```bash
pip install rich psutil
```

## **Quick Start**

To use Pullman, inherit from BaseWorker to define your logic and pass that class to the Orchestrator.
```python
from lambdawalker.pullman.pullman import BaseWorker, Orchestrator  
import time

class MyWorker(BaseWorker):  
    def work(self, payload):  
        # Simulate work  
        time.sleep(payload.get("duration", 1))  
        # Optional: return a result to be stored  
        return {"processed": True}

if __name__ == "__main__":  
    tasks = [{"id": f"T{i}", "payload": {"duration": 0.5}} for i in range(10)]  
  
    orch = Orchestrator(  
        tasks=tasks,  
        worker_class=MyWorker,  
        max_workers=4,  
        session_id="quickstart_session"  
    )  
  
    results = orch.run()
```
## **Feature Showcases**

### **1\. Progress Reporting & Logging**

Workers can report intra-task progress and send logs that appear instantly in the Orchestrator's dashboard.

```python
class DeepWorker(BaseWorker):  
    def work(self, payload):  
        self.log("Starting deep analysis...")  
        for i in range(10):  
            time.sleep(0.5)  
            # Update the UI mini-progress bar  
            self.report_progress((i + 1) / 10)  
            self.log(f"Phase {i+1} complete")
```

### **2\. Shared Memory (The Blackboard)**

Avoid the overhead of serializing heavy data into every task payload. Load it once into the Blackboard.

```python
shared_data = {"model_weights": [0.12, 0.45, 0.78], "config": "production"}

orch = Orchestrator(  
    tasks=tasks,  
    worker_class=MyWorker,  
    blackboard=shared_data  
)

# Inside your worker:  
# weights = self.blackboard["model_weights"]
```

### **3\. Session Recovery & Integrity**

Pullman automatically saves progress. If the process is killed, simply run it again with the same session_id and resume=True.

```python
orch = Orchestrator(  
    tasks=tasks,  
    session_id="batch_v1",  
    resume=True,  # Will skip already PASSED tasks  
    force=False   # Set to True to ignore previous state and start fresh  
)
```

*Note: If the tasks list changes between runs, Pullman will raise a TaskExecutionError to protect you from running a stale session.*

### **4\. Critical Tasks & Priority**

Mark essential tasks as critical. If they fail after all retries, the entire session aborts to save resources. Use priority to control the order of execution.

```python
tasks = [  
    {  
        "id": "INIT_DB",  
        "priority": 0,      # Low number runs first  
        "critical": True,   # Aborts everything if this fails  
        "payload": {}  
    },  
    {  
        "id": "PROCESS_DATA",  
        "priority": 10,  
        "payload": {}  
    }  
]
```

### **5\. Result Aggregation (Reducers)**

Subclass the Orchestrator to define how final data should be consolidated.

```python
class MyOrchestrator(Orchestrator):  
    def reducer(self, results):  
        # Process the results dictionary {task_id: {"status": "...", "data": ...}}  
        total = sum(res["data"]["value"] for res in results.values() if res["status"] == "PASS")  
        return {"final_total": total}
```

## **Configuration Reference**

| Parameter     | Type               | Default            | Description                                                                                      |
|:--------------|:-------------------|:-------------------|:-------------------------------------------------------------------------------------------------|
| tasks         | List\[Dict\]       | Required           | List of task dictionaries with id and optional payload, priority, critical, timeout.             |
| worker\_class | Type\[BaseWorker\] | Required           | Your custom worker implementation.                                                               |
| max\_workers  | int                | 1                  | Static number of worker processes.                                                               |
| worker\_scale | float              | None               | Scale workers based on % of CPU cores (e.g., 0.5 for 50%). Uses higher of max\_workers or scale. |
| retries       | int                | 0                  | Number of times to retry a failed/crashed task.                                                  |
| session\_id   | str                | "default\_session" | Unique ID for progress tracking in .pullman.                                                     |
| show\_ui      | bool               | True               | Whether to display the live Rich dashboard.                                                      |

## **Dashboard Legend**

* **Worker Card**:  
  * **Resources**: Real-time CPU and RAM usage for that specific process.  
  * **Progress**: Visual bar for the current task's internal progress.  
  * **Logs**: The last 2 lines of output from that worker.  
  * **Stats**: Success / Failed / Total tasks handled by that worker.  
  * **Avg**: Trimmed average duration per task (outliers removed).

*Built for developers who need to see what their parallel code is actually doing.*