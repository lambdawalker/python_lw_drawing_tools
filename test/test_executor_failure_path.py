import unittest
import sys
import os
import shutil
from pathlib import Path

# Add src to sys.path to import lambdawaker
sys.path.append(str(Path(__file__).parent.parent / "src"))

from lambdawaker.executor.engine import SubprocessExecutor
from lambdawaker.executor.models import TaskConfig, TaskStatus


class TestExecutorFailurePath(unittest.TestCase):
    def setUp(self):
        self.logs_dir = Path("./logs")
        if self.logs_dir.exists():
            shutil.rmtree(self.logs_dir)

    def tearDown(self):
        if self.logs_dir.exists():
           shutil.rmtree(self.logs_dir)

    def test_failure_and_logging(self):
        config = TaskConfig(
            total_items=10,
            num_workers=1,
            max_retries=1
        )

        failing_task_script = Path(__file__).parent / "failing_task.py"

        def get_command(state):
            return [
                sys.executable,
                str(failing_task_script)
            ]

        executor = SubprocessExecutor(
            config,
            get_command
        )

        executor.run()

        # Worker 0 should have failed
        state = executor.states[0]
        self.assertEqual(state.status, TaskStatus.FAILED)
        
        # Check logs
        log_file = self.logs_dir / "worker_0.log"
        self.assertTrue(log_file.exists(), f"Log file {log_file} should exist")
        
        with open(log_file, "r") as f:
            content = f.read()
            self.assertIn("This is an unrecognized log line 1", content)
            self.assertIn("This is an unrecognized log line 2", content)
            self.assertIn("This is an error in stderr", content)
            # Protocol lines should NOT be in the log
            self.assertNotIn("PROGRESS: 5", content)
            self.assertNotIn("STATUS: RUNNING", content)


if __name__ == "__main__":
    unittest.main()
