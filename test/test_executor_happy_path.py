import unittest
import sys
import os
from pathlib import Path

# Add src to sys.path to import lambdawaker
sys.path.append(str(Path(__file__).parent.parent / "src"))

from lambdawaker.executor.engine import SubprocessExecutor
from lambdawaker.executor.models import TaskConfig, TaskStatus


class TestExecutorHappyPath(unittest.TestCase):
    def test_happy_path(self):
        config = TaskConfig(
            total_items=20,
            num_workers=2,
            max_retries=10  # Increased retries to handle random failures in mock_task.py
        )

        mock_task_script = Path(__file__).parent.parent / "src" / "lambdawaker" / "executor" / "mock_task.py"

        def get_command(state):
            return [
                sys.executable,
                str(mock_task_script),
                "--total", str(state.total)
            ]

        executor = SubprocessExecutor(
            config,
            get_command
        )

        # Run without reporter for simplicity in test
        executor.run()

        # Debug info if fails
        for state in executor.states:
            if state.status != TaskStatus.SUCCESS:
                print(f"Worker {state.worker_id} failed: {state.message}")

        # Verify all workers finished with SUCCESS
        for state in executor.states:
            self.assertEqual(state.status, TaskStatus.SUCCESS)
            self.assertEqual(state.completed, state.total)

        self.assertEqual(executor.global_completed, 20)


if __name__ == "__main__":
    unittest.main()
