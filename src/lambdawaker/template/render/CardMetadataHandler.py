import json
import os
from typing import List, Dict, Any

import requests
import yaml

from lambdawaker.file.path.ensure_directory import ensure_directory_for_file


class CardMetadataHandler:
    def __init__(self, base_url: str, outdir: str):
        self.base_url = base_url
        self.outdir = outdir

    def fetch_template_meta(self, template_name: str) -> Dict[str, Any]:
        raw_meta = requests.get(f"{self.base_url}/render/id_cards/{template_name}/meta.yaml")
        raw_meta.raise_for_status()
        return yaml.safe_load(raw_meta.text)

    def save_object_detection_log(self, record_id: int, template_name: str, elements: List[Dict[str, Any]]):
        obj_detection_log_path = os.path.join(self.outdir, "obj", f"{record_id}_{template_name}.json")
        ensure_directory_for_file(obj_detection_log_path)
        with open(obj_detection_log_path, "w") as f:
            f.write(json.dumps(elements))
