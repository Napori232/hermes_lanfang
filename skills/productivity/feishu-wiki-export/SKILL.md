---
name: feishu-wiki-export
description: "Use when exporting Feishu wiki docs, sheets, and media."
---

# Feishu Wiki Export Workflow

用于从飞书知识库（Wiki）及关联文档、内嵌多维表格（Spreadsheet/Base）、内嵌图片素材中批量提取结构化数据并导出归档。

## 标准提取流程

### 1. 文档解析与内容获取
- 获取 Wiki 节点或 Docx 正文：
  ```bash
  lark-cli docs +fetch --doc <doc_token_or_wiki_token> --doc-format markdown --as user
  ```
- 包含长文档时，按目标小节切分保存，避免上下文过载。

### 2. 内嵌电子表格 / Sheet 数据提取
- 获取电子表格元数据与子表列表：
  ```bash
  lark-cli sheets +workbook-info --spreadsheet-token <token> --as user
  ```
- 读取指定子表单元格范围（注意：`sheets +cells-get` 输出字段为 `valueRange.values`，二维数组）：
  ```bash
  lark-cli sheets +cells-get --spreadsheet-token <token> --range "<sheet_id>!A1:Z100" --as user
  ```

### 3. 内嵌素材与图片下载常见陷阱
- **陷阱：不要使用 `lark-cli drive +download`**
  文档正文内嵌的图片与附件（形如 `img token="TAnmbX..."`）属于 Docx media token，不是 Drive 文件。使用 `drive +download` 会报 HTTP 403 / token lookup failed。
- **陷阱：不要使用 `lark-cli docx` 或传入 `--document-id`**
  CLI 统一使用 `docs` 组，且 `+media-download` 只需要 `--token`：
  ```bash
  lark-cli docs +media-download --token <file_token> --output <local_path> --as user
  ```

### 4. 汇总与归档打包
- 提取完成后，按模块分类保存为清晰命名的 Markdown 与原始媒体文件。
- 使用 Python `zipfile` 快速打包并输出文件清单与体积，便于交付。
