from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class ParsedExamData:
    frame: pd.DataFrame
    subjects: list[str]
