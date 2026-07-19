from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List
import pandas as pd
from classification import QuestionInfo, QuestionType
from lang import LANGUAGES

@dataclass
class QuestionSummary:
    question: QuestionInfo
    table: pd.DataFrame  


def _build_summary_for_series(
    series: pd.Series, question: QuestionInfo, selected_lang="UA"
) -> QuestionSummary:
    v = series.dropna()
    lang = LANGUAGES[selected_lang]

    if v.empty or question.qtype in (QuestionType.OPEN, QuestionType.TECHNICAL):
        table = pd.DataFrame(columns=[lang["option"], lang["count"], "%"])
        return QuestionSummary(question=question, table=table)

    counts = v.astype(str).str.strip().value_counts().sort_index()
    total = counts.sum()
    perc = (counts / total * 100).round(1)

    table = pd.DataFrame(
        {
            lang["option"]: counts.index,
            lang["count"]: counts.values,
            "%": perc.values,
        }
    )

    return QuestionSummary(question=question, table=table)


def build_all_summaries(
    df: pd.DataFrame,
    qinfo: Dict[str, QuestionInfo],
    selected_lang="UA"
) -> List[QuestionSummary]:

    lang = LANGUAGES[selected_lang]
    summaries: List[QuestionSummary] = []

    for col, info in qinfo.items():
        if info.qtype in (QuestionType.OPEN, QuestionType.TECHNICAL):
            continue
        summaries.append(_build_summary_for_series(df[col], info, selected_lang=selected_lang))

    return summaries
