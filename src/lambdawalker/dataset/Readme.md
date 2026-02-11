### Dataset

This module provides tools for managing datasets, specifically focusing on pure Python implementations that support
concurrent reading loads.

#### Key Components

- `Dataset.py`: Base class for dataset implementations.
- `DiskDataset.py`: Implementation of a dataset stored on disk, designed for efficiency and concurrency.
- `DataProvider.py` & `DiskProvider.py`: Interfaces and implementations for providing data from datasets.
- `Record.py`: Defines the structure of individual data records.
- `FieldCaster.py`: Utility for casting fields within records to specific types.
- `ImageSequence.py`: Specialized handler for sequences of images within a dataset.
- `hadlers/`: Contains specific data source handlers, such as `HfDatasetSource.py` for Hugging Face datasets.
