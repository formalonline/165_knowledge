# 系統架構

## 架構摘要

本專案是一個資料轉換 pipeline，不是 SaaS。核心是將官方公開資料轉為 AI 可讀格式。

```text
Official Open Data
        ↓
fetch_165_open_data.py
        ↓
raw CSV
        ↓
normalize_domains.py
        ↓
processed CSV / JSON
        ↓
generate_markdown.py
        ↓
AI-readable Markdown
```

## 元件責任

| 元件 | 責任 |
|---|---|
| `fetch_165_open_data.py` | 下載官方 CSV |
| `normalize_domains.py` | 清理欄位、正規化 domain、去重 |
| `generate_markdown.py` | 產生 AI 可讀文件 |
| `validate_output.py` | 檢查輸出完整性 |
| `update_all.py` | 串接完整流程 |
| GitHub Actions | 定期自動更新 |

## 設計取捨

第一版使用 Markdown / JSON / CSV，而不是資料庫。理由：

- GitHub 可直接呈現。
- 使用者可直接下載。
- AI 可直接讀取。
- 方便開源審查。
- 一人維護成本低。
