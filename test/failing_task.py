import sys


def failing_worker():
    print("PROGRESS: 5")
    print("This is an unrecognized log line 1")
    print("STATUS: RUNNING")
    print("This is an unrecognized log line 2")
    sys.stderr.write("This is an error in stderr\n")
    sys.exit(1)


if __name__ == "__main__":
    failing_worker()
