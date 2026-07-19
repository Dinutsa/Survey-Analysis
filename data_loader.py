"""Module for loading and preprocessing survey data."""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple
import pandas as pd
from lang import LANGUAGES

@dataclass
class LoadedData:
    df: pd.DataFrame
    n_rows: int
    n_cols: int


def load_excels(files: List, selected_lang="UA") -> LoadedData:
    lang = LANGUAGES[selected_lang]

    if not files:
        raise ValueError(lang["value_error"])

    frames = []
    for f in files:
        try:
            frame = pd.read_excel(f)
        except Exception as exc:
            raise ValueError(f"{lang['read_error']}: {getattr(f, 'name', f)}") from exc

        frames.append(frame)

    df = pd.concat(frames, ignore_index=True)

    df.columns = [str(c).strip() for c in df.columns]
    return LoadedData(df=df, n_rows=len(df), n_cols=len(df.columns))


def get_row_bounds(ld: LoadedData) -> Tuple[int, int]:
   
    if ld.n_rows == 0:
        return (0, 0)
    min_row = 2
    max_row = ld.n_rows + 1
    return min_row, max_row


def slice_range(ld: LoadedData, from_row: int, to_row: int, selected_lang="UA") -> pd.DataFrame:
    lang = LANGUAGES[selected_lang]

    if from_row > to_row:
        raise ValueError(lang["first_row_error"])
    start_idx = from_row - 2
    end_idx = to_row - 2  # added
    if start_idx < 0 or end_idx >= ld.n_rows:
        raise ValueError(lang["range_error"])

    return ld.df.iloc[start_idx : end_idx + 1].copy()
