import os
from .ensure_directory import ensure_directory_for_file


class LazyFileWriter:
    def __init__(self, file_path: str, mode: str = "w"):
        self.file_path = file_path
        self.mode = mode
        self.file = None

    def write(self, content: str):
        if self.file is None:
            ensure_directory_for_file(self.file_path)
            self.file = open(self.file_path, self.mode, encoding="utf-8")
        self.file.write(content)

    def flush(self):
        if self.file:
            self.file.flush()

    def close(self):
        if self.file:
            self.file.close()
            self.file = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
