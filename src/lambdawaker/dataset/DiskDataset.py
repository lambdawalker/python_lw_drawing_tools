import pathlib
import random
from typing import Dict, Any, Union, Optional

import yaml

from lambdawaker.dataset.DataProvider import DataProvider
from lambdawaker.dataset.Dataset import Dataset
from lambdawaker.dataset.DiskProvider import DiskProvider
from lambdawaker.dataset.FieldCaster import FieldCaster
from lambdawaker.dataset.Record import Record


class DiskDataset(Dataset):
    """
    A dataset implementation that stores and retrieves data from the local disk.

    This class uses a manifest file (e.g., 'manifest.yaml') to define the structure
    of the dataset, including the fields and their storage locations.
    """

    def __init__(self, path: str, provider: Optional[DataProvider] = None, read_only: bool = False):
        """
        Initializes the dataset.

        Args:
            provider (Optional[DataProvider], optional): A data provider instance.
                If no provider is given, it defaults to a DiskProvider.
            read_only (bool, optional): If True, the dataset cannot be modified. Defaults to False.
        """
        self.provider = provider if provider is not None else DiskProvider()
        self.manifest = None
        self.record_ids = []
        self.extensions = {} # name: extension
        self.read_only = read_only
        self.id = None
        self.load(path)

    def load(self, root_path: str, manifest_name: str = "manifest.yaml"):
        """
        Loads the dataset from the specified root path and manifest file.

        Args:
            root_path (str): The root directory of the dataset.
            manifest_name (str, optional): The name of the manifest file. Defaults to "manifest.yaml".
        """
        self.provider.pointTo(root_path)

        # 1. Load the YAML manifest using the provider
        raw_manifest = self.provider.serve(manifest_name)
        self.manifest = yaml.safe_load(raw_manifest)
        self.id = self.manifest.get('id')

        # 2. Synchronize the internal ID list
        self._refresh_ids()

    def _refresh_ids(self):
        """Scans all fields' directories to find valid Record IDs and detect extensions."""
        if not self.manifest or not self.manifest.get('fields'):
            return

        cache_name = ".dataset_cache.yaml"
        if self.provider.exists(cache_name):
            try:
                raw_cache = self.provider.serve(cache_name)
                cache = yaml.safe_load(raw_cache)
                self.record_ids = cache.get('record_ids', [])
                self.extensions = cache.get('extensions', {})
                return
            except Exception:
                # If cache is corrupted, we just ignore it and refresh
                pass

        self.record_ids = []
        self.extensions = {}
        for field in self.manifest['fields']:
            folder = field.get('source')
            name = field.get('name')
            if not folder:
                continue
            
            files = self.provider.list(folder)
            for f in files:
                p = pathlib.Path(f)
                stem = p.stem
                
                if name not in self.extensions:
                    self.extensions[name] = p.suffix

                if stem not in self.record_ids:
                    self.record_ids.append(stem)
        
        self.record_ids.sort()
        self._save_cache()

    def _save_cache(self):
        """Saves the current record_ids and extensions to a cache file."""
        if self.read_only:
            return
            
        cache_name = ".dataset_cache.yaml"
        cache_data = {
            'record_ids': self.record_ids,
            'extensions': self.extensions
        }
        content = yaml.dump(cache_data, default_flow_style=False)
        self.provider.store(content, cache_name)

    def _find_file_for_id(self, field: dict, record_id: str) -> str:
        """Helper to find the actual filename for an ID using stored extensions."""
        folder = field.get('source')
        name = field.get('name')

        ext = self.extensions.get(name)
        if ext:
            path = f"{folder}/{record_id}{ext}"
            if self.provider.exists(path):
                return path

        raise FileNotFoundError(f"No file found for ID '{record_id}' in '{folder}'")

    def record_by_name(self, record_id: str) -> Record:
        """
        Retrieves a single record from the dataset by its ID.

        Args:
            record_id (str): The ID of the record to retrieve.

        Returns:
            Dict[str, Any]: A dictionary containing the data for the requested record.
        """
        result = {"id": record_id}

        for field in self.manifest['fields']:
            name = field['name']

            try:
                rel_path = self._find_file_for_id(field, record_id)
                raw_data = self.provider.serve(rel_path)

                # Using the new FieldCaster
                result[name] = FieldCaster.cast(
                    raw_data, field['type'], rel_path
                )
            except FileNotFoundError:
                # If a file is missing for a field, we just skip it for this record
                continue

        return Record(result)

    def random(self) -> Record:
        """
        Retrieves a random record from the dataset.

        Returns:
            Dict[str, Any]: A dictionary containing the data for a random record.
        """
        if not self.record_ids:
            raise IndexError("Dataset is empty.")
        return self.record_by_name(random.choice(self.record_ids))

    def insert(self, record_id: str, data: Dict[str, Any]):
        """
        Inserts or updates a record in the dataset.

        Args:
            record_id (str): The ID of the record to insert or update.
            data (Dict[str, Any]): The data for the record.
        """
        if self.read_only:
            raise RuntimeError("Cannot insert into read-only dataset.")

        for field in self.manifest['fields']:
            name = field['name']
            if name not in data: continue

            # Use FieldCaster to turn Python object into bytes
            content = FieldCaster.serialize(data[name], field['type'])

            # Determine extension
            ext = self.extensions.get(name)
            if not ext:
                ext_map = {
                    'json': '.json',
                    'yaml': '.yaml',
                    'str': '.txt',
                    'int': '.txt',
                    'float': '.txt',
                    'xml': '.xml',
                    'svgDoc': '.svg',
                    'numpy': '.npy',
                    'PilImage': '.png',
                    'npImage': '.png'
                }
                ext = ext_map.get(field['type'], '.bin')
                self.extensions[name] = ext

            path = f"{field['source']}/{record_id}{ext}"
            self.provider.store(content, path)

        if record_id not in self.record_ids:
            self.record_ids.append(record_id)
            self.record_ids.sort()
            self._save_cache()

    def delete(self, record_id: str):
        """
        Deletes a record from the dataset.

        Args:
            record_id (str): The ID of the record to delete.
        """
        if self.read_only:
            raise RuntimeError("Cannot insert into read-only dataset.")

        for field in self.manifest['fields']:
            try:
                path = self._find_file_for_id(field, record_id)
                self.provider.delete(path)
            except FileNotFoundError:
                continue
        self.record_ids = [rid for rid in self.record_ids if rid != record_id]
        self._save_cache()

    def __len__(self) -> int:
        """
        Returns the number of records in the dataset.

        Returns:
            int: The number of records.
        """
        return len(self.record_ids)

    def __getitem__(self, key: Union[int, str]) -> Record:
        """
        Allows accessing records using dataset[index] or dataset['record_id'].

        Args:
            key: If int, retrieves by index in the discovered record_ids.
                 If str, retrieves by the specific record ID.
        """
        if isinstance(key, int):
            if key < 0:
                key = key % len(self.record_ids)

            if key >= len(self.record_ids):
                raise IndexError(f"Dataset index {key} out of range.")

            return self.record_by_name(self.record_ids[key])


        elif isinstance(key, str):
            if "/" in key:
                return self.__str__getitem__(key)
            return self.record_by_name(key)

        else:
            raise TypeError("Key must be an integer index or a string Record ID.")

    def __str__getitem__(self, item):
        path = item.split("/")

        split = self
        key = path[1]
        field = None
        if len(path) > 2:
            field = path[2]

        if key == "":
            return split
        elif key == "len":
            return len(split)

        elif key == "random":
            limit = len(split)
            record = split[random.randint(0, limit)]
            if field is None:
                return record
            return record[field]

        elif key.isdigit():
            key = int(key)
            path_size = len(path)
            if path_size == 2:
                return split[key]

            elif path_size == 3:
                field = path[2]
                return split[key][field]

        raise ValueError(f"Unsupported data type: {path}")
