import os


def ensure_directory_for_file(file_path):
    if file_path is not None:
        output_dir = os.path.dirname(file_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
