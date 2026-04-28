# score_analysis

学生成绩名次对比分析工具：输入两份成绩单（Excel），输出对比结果（Excel），用于观察学生在两次考试中的**年级名次变化**，并生成各指标的 **TopK 进步/退步榜单**。

## 本地命令行使用（推荐）

### 环境准备

- Python 3
- 安装依赖（仓库根目录执行）：

```bash
py -m pip install -r requirements-backend.txt
```

> 说明：本项目读取 `.xls` 依赖 `xlrd==2.0.1`，输出 `.xlsx` 依赖 `openpyxl`。

### 运行命令

在仓库根目录执行：

```bash
py .\analyze_scores.py --first "75第一学期期末总分名次.xls" --second "75第二学期学生总分名次.xls" --output "75对比分析.xlsx"
```

参数说明：

- `--first`：第一份成绩单路径（相对/绝对路径均可）
- `--second`：第二份成绩单路径（相对/绝对路径均可）
- `--output`：输出 Excel 路径（建议 `.xlsx`）
- `--top-k`：可选。每个指标输出 TopK 名单，默认 `10`，且必须 \(\ge 1\)

示例（TopK=20）：

```bash
py .\analyze_scores.py --first "75第一学期期末总分名次.xls" --second "75第二学期学生总分名次.xls" --output "75对比分析_top20.xlsx" --top-k 20
```

### 不推荐的入口

`score_analysis/cli.py` 仅提供 `main()` 供其它入口调用，**不作为可直接执行的模块入口**。请统一使用 `analyze_scores.py` 运行。

## 输出文件说明

输出的 `.xlsx` 通常包含：

- `sheet1`：每个学生、每个科目的两次年级排名与名次变化
- `sheet2`：按“指标”聚合的 TopK 榜单（进步/退步）

## 常见问题

### 1) 找不到文件 / 路径含空格

- 优先在仓库根目录运行命令
- 路径包含空格时请加双引号，例如 `--first "C:\path with space\a.xls"`

### 2) `.xls` 读取失败

- 确认已安装依赖：

```bash
py -m pip install -r requirements-backend.txt
```

- 如果你的源文件其实是 `.xlsx`，建议直接使用 `.xlsx`（本项目同样支持）

## 相关文档

- 后端 API：`backend_mvp/README.md`
- 小程序：`miniapp_mvp/README.md`
- 云部署：`deploy/tencentcloud/README.md`

