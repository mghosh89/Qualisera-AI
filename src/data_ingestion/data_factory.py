"""
Factory pattern for loading different healthcare datasets
"""
from typing import Optional, Dict, Any
from .synthea_loader import SyntheaDataLoader
from .nih_loader import NIHDataLoader
from .fhir_loader import FHIRDataLoader


class DataFactory:
    """Factory class to create appropriate data loaders"""

    _loaders = {
        "synthea": SyntheaDataLoader,
        "nih": NIHDataLoader,
        "fhir": FHIRDataLoader
    }

    @classmethod
    def get_loader(cls, dataset_type: str, config: Optional[Dict[str, Any]] = None):
        """
        Get appropriate data loader for the dataset type

        Args:
            dataset_type: Type of dataset (synthea, nih, fhir)
            config: Configuration dictionary for the loader

        Returns:
            Instance of the appropriate data loader
        """
        if dataset_type.lower() not in cls._loaders:
            raise ValueError(
                f"Unsupported dataset type: {dataset_type}. "
                f"Supported types: {list(cls._loaders.keys())}"
            )

        loader_class = cls._loaders[dataset_type.lower()]
        return loader_class(config or {})

    @classmethod
    def list_supported_datasets(cls) -> list:
        """List all supported dataset types"""
        return list(cls._loaders.keys())