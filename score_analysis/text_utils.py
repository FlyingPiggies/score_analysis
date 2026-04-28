from __future__ import annotations

import re

import pandas as pd

from .constants import (
    EMPTY_VALUE_MARKERS,
    METRIC_CLASS_RANK,
    METRIC_SCORE,
    METRIC_YEAR_RANK,
    STUDENT_ID_DIGITS_PATTERN,
    SUBJECT_ALIASES,
    SUBJECT_TOTAL_SCORE,
    TOTAL_SUBJECT_ALIASES,
)


def clean_text(value: object) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if text.lower() in EMPTY_VALUE_MARKERS:
        return ""
    return text


def normalize_subject_name(subject: str) -> str:
    base = clean_text(subject)
    if base in SUBJECT_ALIASES:
        return SUBJECT_ALIASES[base]
    if base in TOTAL_SUBJECT_ALIASES:
        return SUBJECT_TOTAL_SCORE
    return base


def normalize_student_id(value: object) -> str:
    text = clean_text(value)
    if not text:
        return ""
    try:
        numeric_value = float(text)
    except ValueError:
        return text if re.fullmatch(STUDENT_ID_DIGITS_PATTERN, text) else ""
    if numeric_value.is_integer():
        return str(int(numeric_value))
    return text


def classify_metric_type(metric_name: str, score_keywords: set[str], year_rank_keywords: set[str], class_rank_keywords: set[str]) -> str:
    metric = clean_text(metric_name)
    if metric in score_keywords:
        return METRIC_SCORE
    if metric in year_rank_keywords:
        return METRIC_YEAR_RANK
    if metric in class_rank_keywords:
        return METRIC_CLASS_RANK
    return ""


def format_rank_change_text(change_value: object) -> str:
    if pd.isna(change_value):
        return "无数据"
    change_int = int(change_value)
    if change_int > 0:
        return f"进步{change_int}名"
    if change_int < 0:
        return f"退步{abs(change_int)}名"
    return "无变化"
