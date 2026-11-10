"""
Data Ingestion Module for Qualisera AI
Supports multiple healthcare data sources
"""
from .data_factory import DataFactory
from .synthea_loader import SyntheaDataLoader
from .nih_loader import NIHDataLoader
from .fhir_loader import FHIRDataLoader

__all__ = [
    "DataFactory",
    "SyntheaDataLoader",
    "NIHDataLoader",
    "FHIRDataLoader"
]