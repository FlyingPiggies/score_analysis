from __future__ import annotations

import argparse
from pathlib import Path

from .constants import TOP_K_COUNT, TOP_K_MIN
from .service import run_analysis


def validate_top_k(value: str) -> int:
    parsed = int(value)
    if parsed < TOP_K_MIN:
        raise argparse.ArgumentTypeError(f"--top-k 必须大于等于 {TOP_K_MIN}")
    return parsed


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="学生成绩名次对比分析工具（按年级名次变化）")
    parser.add_argument(
        "--first",
        dest="first_exam_filename",
        required=True,
        help="第一份成绩单路径（支持相对路径或绝对路径）",
    )
    parser.add_argument(
        "--second",
        dest="second_exam_filename",
        required=True,
        help="第二份成绩单路径（支持相对路径或绝对路径）",
    )
    parser.add_argument(
        "--output",
        dest="output_filename",
        required=True,
        help="输出 Excel 路径（例如：成绩对比.xlsx）",
    )
    parser.add_argument(
        "--top-k",
        dest="top_k",
        type=validate_top_k,
        default=TOP_K_COUNT,
        help=f"每个指标输出 TopK 名单，默认 {TOP_K_COUNT}",
    )
    return parser.parse_args()


def main() -> None:
    working_directory = Path(__file__).resolve().parent.parent
    cli_args = parse_arguments()
    generated_file = run_analysis(
        base_dir=working_directory,
        first_exam_filename=cli_args.first_exam_filename,
        second_exam_filename=cli_args.second_exam_filename,
        output_filename=cli_args.output_filename,
        top_k=cli_args.top_k,
    )
    print(f"已生成结果文件：{generated_file}")
