from __future__ import annotations

from typing import Sequence

import pandas as pd

from .constants import (
    COLUMN_MATCH_KEY,
    COLUMN_NAME,
    COLUMN_POSITION,
    COLUMN_STUDENT_ID,
    METRIC_CHANGE_DESCRIPTION,
    METRIC_RANK_CHANGE,
    METRIC_YEAR_RANK,
    OUTPUT_COLUMN_INDICATOR,
    OUTPUT_COLUMN_TYPE,
    SEMESTER_FIRST,
    SEMESTER_SECOND,
    TOP_K_COUNT,
    TOP_TYPE_IMPROVE,
    TOP_TYPE_REGRESS,
)
from .models import ParsedExamData
from .text_utils import format_rank_change_text


def build_comparison_sheet(first_exam: ParsedExamData, second_exam: ParsedExamData) -> tuple[pd.DataFrame, list[str]]:
    first_df = first_exam.frame.copy()
    second_df = second_exam.frame.copy()

    common_subjects = [
        subject
        for subject in first_exam.subjects
        if subject in second_exam.subjects
        and f"{subject}_{METRIC_YEAR_RANK}" in first_df.columns
        and f"{subject}_{METRIC_YEAR_RANK}" in second_df.columns
    ]
    if not common_subjects:
        raise ValueError("两份成绩单没有可比较的共同科目。")

    selected_columns = [COLUMN_MATCH_KEY, COLUMN_NAME, COLUMN_STUDENT_ID]
    for subject in common_subjects:
        selected_columns.append(f"{subject}_{METRIC_YEAR_RANK}")

    first_selected = first_df[selected_columns].copy()
    second_selected = second_df[selected_columns].copy()

    merged = pd.merge(
        first_selected,
        second_selected,
        how="inner",
        on=[COLUMN_MATCH_KEY],
        suffixes=(f"_{SEMESTER_FIRST}", f"_{SEMESTER_SECOND}"),
    )
    if merged.empty:
        raise ValueError("两份成绩单按“学号优先，缺失则姓名”匹配后没有重叠学生。")

    output_columns = [COLUMN_NAME, COLUMN_STUDENT_ID]
    first_name_col = f"{COLUMN_NAME}_{SEMESTER_FIRST}"
    second_name_col = f"{COLUMN_NAME}_{SEMESTER_SECOND}"
    first_id_col = f"{COLUMN_STUDENT_ID}_{SEMESTER_FIRST}"
    second_id_col = f"{COLUMN_STUDENT_ID}_{SEMESTER_SECOND}"

    result = pd.DataFrame()
    result[COLUMN_NAME] = merged[first_name_col].fillna("").astype(str)
    fallback_name = merged[second_name_col].fillna("").astype(str)
    result[COLUMN_NAME] = result[COLUMN_NAME].mask(result[COLUMN_NAME] == "", fallback_name)

    primary_id = merged[first_id_col].fillna("").astype(str)
    fallback_id = merged[second_id_col].fillna("").astype(str)
    result[COLUMN_STUDENT_ID] = primary_id.mask(primary_id == "", fallback_id)

    for subject in common_subjects:
        rank_first_col = f"{subject}_{METRIC_YEAR_RANK}_{SEMESTER_FIRST}"
        rank_second_col = f"{subject}_{METRIC_YEAR_RANK}_{SEMESTER_SECOND}"
        rank_diff_col = f"{subject}_{METRIC_RANK_CHANGE}"

        result[f"{subject}_{SEMESTER_FIRST}{METRIC_YEAR_RANK}"] = merged[rank_first_col]
        result[f"{subject}_{SEMESTER_SECOND}{METRIC_YEAR_RANK}"] = merged[rank_second_col]
        result[rank_diff_col] = merged[rank_first_col] - merged[rank_second_col]

        output_columns.extend(
            [
                f"{subject}_{SEMESTER_FIRST}{METRIC_YEAR_RANK}",
                f"{subject}_{SEMESTER_SECOND}{METRIC_YEAR_RANK}",
                rank_diff_col,
            ]
        )

    return result[output_columns].copy(), common_subjects


def build_top_records(
    comparison_sheet_df: pd.DataFrame,
    subject: str,
    ascending: bool,
    top_k: int = TOP_K_COUNT,
) -> pd.DataFrame:
    rank_change_col = f"{subject}_{METRIC_RANK_CHANGE}"
    base = comparison_sheet_df[[COLUMN_NAME, COLUMN_STUDENT_ID, rank_change_col]].dropna(subset=[rank_change_col])
    if base.empty:
        return pd.DataFrame(columns=[COLUMN_NAME, COLUMN_STUDENT_ID, rank_change_col])
    sorted_df = base.sort_values(by=rank_change_col, ascending=ascending).head(top_k).copy()
    sorted_df[COLUMN_POSITION] = list(range(1, len(sorted_df) + 1))
    return sorted_df


def build_top_sheet(
    comparison_sheet_df: pd.DataFrame,
    subjects: Sequence[str],
    top_k: int = TOP_K_COUNT,
) -> pd.DataFrame:
    records: list[dict[str, object]] = []
    for subject in subjects:
        improve_df = build_top_records(comparison_sheet_df, subject=subject, ascending=False, top_k=top_k)
        regress_df = build_top_records(comparison_sheet_df, subject=subject, ascending=True, top_k=top_k)
        for title, source in [(TOP_TYPE_IMPROVE, improve_df), (TOP_TYPE_REGRESS, regress_df)]:
            for _, row in source.iterrows():
                rank_change_col = f"{subject}_{METRIC_RANK_CHANGE}"
                rank_change_value = row[rank_change_col]
                records.append(
                    {
                        OUTPUT_COLUMN_INDICATOR: subject,
                        OUTPUT_COLUMN_TYPE: title,
                        COLUMN_POSITION: int(row[COLUMN_POSITION]),
                        COLUMN_NAME: row[COLUMN_NAME],
                        COLUMN_STUDENT_ID: row[COLUMN_STUDENT_ID],
                        METRIC_RANK_CHANGE: rank_change_value,
                        METRIC_CHANGE_DESCRIPTION: format_rank_change_text(rank_change_value),
                    }
                )

    output_columns = [
        OUTPUT_COLUMN_INDICATOR,
        OUTPUT_COLUMN_TYPE,
        COLUMN_POSITION,
        COLUMN_NAME,
        COLUMN_STUDENT_ID,
        METRIC_RANK_CHANGE,
        METRIC_CHANGE_DESCRIPTION,
    ]
    return pd.DataFrame(records, columns=output_columns)
