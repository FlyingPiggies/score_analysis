from __future__ import annotations

from pathlib import Path

from .analyzer import build_comparison_sheet, build_top_sheet
from .constants import TOP_K_COUNT
from .exam_parser import parse_exam
from .report_writer import write_workbook


def resolve_path(base_dir: Path, file_path: str) -> Path:
    resolved = Path(file_path)
    if not resolved.is_absolute():
        resolved = base_dir / resolved
    return resolved


def run_analysis(
    base_dir: Path,
    first_exam_filename: str,
    second_exam_filename: str,
    output_filename: str,
    top_k: int = TOP_K_COUNT,
) -> Path:
    first_exam_path = resolve_path(base_dir, first_exam_filename)
    second_exam_path = resolve_path(base_dir, second_exam_filename)
    output_path = resolve_path(base_dir, output_filename)

    if not first_exam_path.exists():
        raise FileNotFoundError(f"未找到文件：{first_exam_path}")
    if not second_exam_path.exists():
        raise FileNotFoundError(f"未找到文件：{second_exam_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    first_exam = parse_exam(first_exam_path)
    second_exam = parse_exam(second_exam_path)

    comparison_sheet_df, subjects = build_comparison_sheet(first_exam, second_exam)
    top_sheet_df = build_top_sheet(comparison_sheet_df, subjects, top_k=top_k)
    write_workbook(output_path, comparison_sheet_df, top_sheet_df)
    return output_path
