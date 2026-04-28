from __future__ import annotations

from pathlib import Path
from typing import Sequence

import pandas as pd

from .constants import (
    CLASS_RANK_KEYWORDS,
    COLUMN_CLASS_NAME,
    COLUMN_MATCH_KEY,
    COLUMN_NAME,
    COLUMN_STUDENT_ID,
    COLUMN_STUDENT_REGISTRATION_ID,
    MAIN_HEADER_STOP_WORDS,
    MAX_HEADER_SCAN_ROWS,
    METRIC_SCORE,
    METRIC_YEAR_RANK,
    SCORE_KEYWORDS,
    SUBJECT_TOTAL_SCORE,
    YEAR_RANK_KEYWORDS,
)
from .models import ParsedExamData
from .text_utils import classify_metric_type, clean_text, normalize_student_id, normalize_subject_name


def detect_header_start_row(raw_df: pd.DataFrame) -> int:
    upper_bound = min(len(raw_df), MAX_HEADER_SCAN_ROWS)
    for index in range(upper_bound):
        row_values = [clean_text(item) for item in raw_df.iloc[index].tolist()]
        has_name = COLUMN_NAME in row_values
        has_student_id = COLUMN_STUDENT_ID in row_values or COLUMN_STUDENT_REGISTRATION_ID in row_values
        if has_name and has_student_id:
            return index
    raise ValueError("无法识别表头起始行：未找到包含“姓名”和“学号/学籍号”的行。")


def detect_header_depth(raw_df: pd.DataFrame, header_start_row: int) -> int:
    candidate_row_index = header_start_row + 1
    if candidate_row_index >= len(raw_df):
        return 1
    candidate_values = {clean_text(item) for item in raw_df.iloc[candidate_row_index].tolist()}
    rank_or_score_tokens = SCORE_KEYWORDS | YEAR_RANK_KEYWORDS | CLASS_RANK_KEYWORDS
    if candidate_values.intersection(rank_or_score_tokens):
        return 2
    return 1


def forward_fill_header(values: Sequence[object]) -> list[str]:
    result: list[str] = []
    carry = ""
    for value in values:
        current = clean_text(value)
        if current and current.lower() not in MAIN_HEADER_STOP_WORDS:
            carry = current
            result.append(current)
        else:
            result.append(carry)
    return result


def build_raw_column_names(raw_df: pd.DataFrame, header_start: int, header_depth: int) -> list[str]:
    main_header = raw_df.iloc[header_start].tolist()
    sub_header = raw_df.iloc[header_start + 1].tolist() if header_depth == 2 else [""] * len(main_header)
    filled_main = forward_fill_header(main_header)
    raw_column_names: list[str] = []
    passthrough_columns = {COLUMN_NAME, COLUMN_STUDENT_ID, COLUMN_STUDENT_REGISTRATION_ID, COLUMN_CLASS_NAME}
    for main_value, sub_value in zip(filled_main, sub_header):
        main_text = clean_text(main_value)
        sub_text = clean_text(sub_value)
        if not main_text and not sub_text:
            raw_column_names.append("")
            continue
        if main_text in passthrough_columns and not sub_text:
            raw_column_names.append(main_text)
            continue
        if sub_text:
            raw_column_names.append(f"{main_text}_{sub_text}")
            continue
        raw_column_names.append(main_text)
    return raw_column_names


def normalize_column_name(raw_column_name: str) -> str:
    raw_name = clean_text(raw_column_name)
    if not raw_name:
        return ""
    passthrough_columns = {COLUMN_NAME, COLUMN_STUDENT_ID, COLUMN_STUDENT_REGISTRATION_ID, COLUMN_CLASS_NAME}
    if raw_name in passthrough_columns:
        return raw_name
    if "_" not in raw_name:
        return normalize_subject_name(raw_name)
    subject_part, metric_part = raw_name.split("_", maxsplit=1)
    subject = normalize_subject_name(subject_part)
    metric_type = classify_metric_type(
        metric_part,
        score_keywords=SCORE_KEYWORDS,
        year_rank_keywords=YEAR_RANK_KEYWORDS,
        class_rank_keywords=CLASS_RANK_KEYWORDS,
    )
    if metric_type:
        return f"{subject}_{metric_type}"
    return f"{subject}_{metric_part}"


def coerce_numeric_columns(df: pd.DataFrame, columns: Sequence[str]) -> None:
    for column in columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")


def extract_subjects(columns: Sequence[str]) -> list[str]:
    subjects = set()
    for column in columns:
        if column.endswith(f"_{METRIC_SCORE}") or column.endswith(f"_{METRIC_YEAR_RANK}"):
            subjects.add(column.rsplit("_", maxsplit=1)[0])
    if SUBJECT_TOTAL_SCORE in subjects:
        ordered_subjects = sorted(subject for subject in subjects if subject != SUBJECT_TOTAL_SCORE)
        ordered_subjects.append(SUBJECT_TOTAL_SCORE)
        return ordered_subjects
    return sorted(subjects)


def ensure_required_columns(df: pd.DataFrame, required_columns: Sequence[str], file_path: Path) -> None:
    missing = [column for column in required_columns if column not in df.columns]
    if missing:
        joined = "、".join(missing)
        raise ValueError(f"文件 {file_path.name} 缺少必要字段：{joined}")


def build_match_key(student_name: str, student_id: str) -> str:
    if student_id:
        return f"学号:{student_id}"
    return f"姓名:{student_name}"


def validate_match_key_uniqueness(df: pd.DataFrame, file_path: Path) -> None:
    duplicate_mask = df[COLUMN_MATCH_KEY].duplicated(keep=False)
    if not duplicate_mask.any():
        return
    duplicates = df.loc[duplicate_mask, [COLUMN_NAME, COLUMN_STUDENT_ID, COLUMN_MATCH_KEY]].drop_duplicates()
    duplicate_text = "；".join(
        f"{row[COLUMN_NAME]}({row[COLUMN_STUDENT_ID] if row[COLUMN_STUDENT_ID] else '无学号'})"
        for _, row in duplicates.iterrows()
    )
    raise ValueError(f"文件 {file_path.name} 存在重复匹配键：{duplicate_text}")


def parse_exam(file_path: Path) -> ParsedExamData:
    raw_df = pd.read_excel(file_path, sheet_name=0, header=None, engine="xlrd")
    header_start = detect_header_start_row(raw_df)
    header_depth = detect_header_depth(raw_df, header_start)
    raw_column_names = build_raw_column_names(raw_df, header_start, header_depth)

    data_start = header_start + header_depth
    data_df = raw_df.iloc[data_start:].copy()
    data_df.columns = raw_column_names
    data_df = data_df.loc[:, [column for column in data_df.columns if clean_text(column)]]
    data_df = data_df.dropna(how="all").copy()

    renamed_columns: dict[str, str] = {}
    for source_column in data_df.columns:
        normalized_name = normalize_column_name(source_column)
        if normalized_name:
            renamed_columns[source_column] = normalized_name
    data_df = data_df.rename(columns=renamed_columns)

    if COLUMN_STUDENT_ID not in data_df.columns and COLUMN_STUDENT_REGISTRATION_ID in data_df.columns:
        data_df[COLUMN_STUDENT_ID] = data_df[COLUMN_STUDENT_REGISTRATION_ID]

    ensure_required_columns(data_df, [COLUMN_NAME, COLUMN_STUDENT_ID], file_path)

    data_df[COLUMN_NAME] = data_df[COLUMN_NAME].map(clean_text)
    data_df[COLUMN_STUDENT_ID] = data_df[COLUMN_STUDENT_ID].map(normalize_student_id)
    subject_columns = [
        column
        for column in data_df.columns
        if column.endswith(f"_{METRIC_SCORE}") or column.endswith(f"_{METRIC_YEAR_RANK}")
    ]
    coerce_numeric_columns(data_df, subject_columns)
    subjects = extract_subjects(data_df.columns)

    total_rank_column = f"{SUBJECT_TOTAL_SCORE}_{METRIC_YEAR_RANK}"
    ensure_required_columns(data_df, [total_rank_column], file_path)
    data_df = data_df[data_df[COLUMN_NAME] != ""].copy()
    data_df = data_df[data_df[total_rank_column].notna()].copy()
    data_df[COLUMN_MATCH_KEY] = data_df.apply(
        lambda row: build_match_key(row[COLUMN_NAME], row[COLUMN_STUDENT_ID]),
        axis=1,
    )
    validate_match_key_uniqueness(data_df, file_path)
    return ParsedExamData(frame=data_df, subjects=subjects)
