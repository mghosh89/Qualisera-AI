"""Synthea CSV loader (§5.2). Returns DataFrames + counts. No validation."""
import pandas as pd
from pathlib import Path


def load(directory: str):
    d = Path(directory)
    out = {}
    for name in ("patients", "observations", "conditions", "medications"):
        f = d / f"{name}.csv"
        if f.exists():
            out[name] = pd.read_csv(f)
    return out