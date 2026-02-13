import mimetypes
from datetime import datetime
from pathlib import Path
from typing import Union, List, Dict

import yaml
from fastapi import HTTPException



class FileMetadataHandler:
    def __init__(self, root_path: Union[str, Path]):
        self.root = Path(root_path).resolve()
        if not self.root.exists():
            raise ValueError(f"Root path {root_path} does not exist.")

    def get_template_summary(self) -> Dict:
        templates = []
        total_samples = 0

        # Based on description: [site_path]/id_cards/A/meta.yaml
        # We iterate over root/id_cards instead of searching files recursively
        id_cards_root = self.root / "id_cards"
        
        if id_cards_root.exists() and id_cards_root.is_dir():
            for template_dir in id_cards_root.iterdir():
                if not template_dir.is_dir() or template_dir.name.startswith("_"):
                    continue
                
                meta_path = template_dir / "meta.yaml"
                if not meta_path.exists():
                    continue

                try:
                    with open(meta_path, 'r') as f:
                        meta_data = yaml.safe_load(f)
                    
                    if meta_data and isinstance(meta_data, dict):
                        samples = meta_data.get("samples", 0)
                        # Template name is relative to root
                        name = str(template_dir.relative_to(self.root)).replace("\\", "/")
                        
                        templates.append({
                            "name": name,
                            "samples": samples
                        })
                        total_samples += samples
                except Exception:
                    # Skip invalid YAML or files we can't read
                    continue

        return {
            "total": total_samples,
            "templates": templates
        }

    def _get_metadata(self, entry: Path) -> Dict:
        """Helper to extract metadata for a single file or directory."""
        stats = entry.stat()

        mimetype = "inode/directory" if entry.is_dir() else mimetypes.guess_type(entry)[0]

        return {
            "name": entry.name,
            "size": stats.st_size,
            "st_mtime": datetime.fromtimestamp(stats.st_mtime).isoformat(),
            "path": str(entry.relative_to(self.root)),
            "mimetype": mimetype,
            "is_dir": entry.is_dir(),
            "extension": entry.suffix if entry.is_file() else None,
        }

    def __call__(self, relative_path: str = "") -> Union[List[Dict], Dict]:
        # 1. Resolve target path and prevent directory traversal
        target = (self.root / relative_path.lstrip("/")).resolve()

        if not target.exists():
            raise HTTPException(status_code=404, detail="Path not found")

        if not str(target).startswith(str(self.root)):
            raise HTTPException(status_code=403, detail="Access denied")

        # 2. Logic for Directories
        if target.is_dir():
            return [self._get_metadata(item) for item in target.iterdir()]

        # 3. Logic for Files
        return self._get_metadata(target)
