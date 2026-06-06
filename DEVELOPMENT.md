# 開發文件：Anti Scam AI Knowledge TW

版本：v0.1.0  
日期：2026-06-06  
目標：建立一個可一人維護、可自動更新、可給 AI/RAG 讀取的台灣防詐騙知識包。

## 1. 專案目標

本專案不是瀏覽器外掛，也不是完整聊天機器人。第一版只做「官方防詐公開資料 → 結構化資料 → Markdown 知識包」的自動化流程。

核心目標：

1. 自動取得官方公開防詐資料。
2. 清理網址、網域、資料欄位與重複資料。
3. 產生 AI 可讀 Markdown。
4. 產生 RAG 可用 JSON / CSV。
5. 使用 GitHub Actions 定期自動更新。
6. 提供 AGENTS.md 與提示詞，讓 Codex / Claude Code / Cursor / ChatGPT 能直接使用。

## 2. 產品定位

推薦 repo 名稱：

```text
anti-scam-ai-knowledge-tw
```

一句話描述：

```text
Taiwan Anti-Scam AI Knowledge Pack: automatically converts official 165 anti-scam open data into AI-readable Markdown, JSON, and CSV.
```

中文描述：

```text
台灣防詐騙 AI 知識包：自動抓取 165 與政府 Open Data，整理成 Markdown、JSON、CSV，讓任何 AI 都能讀取最新防詐知識。
```

## 3. MVP 範圍

### 必做

- 讀取 165 涉詐網站 CSV。
- 正規化 URL / domain。
- 輸出 `scam-domains.csv`。
- 輸出 `scam-domains.json`。
- 輸出 `knowledge/suspicious-domains.md`。
- 輸出 `knowledge/anti-scam-latest.md`。
- 提供 GitHub Actions 每日更新。
- 提供安全提示詞 `anti-scam-agent-prompt.md`。

### 暫不做

- Chrome Extension。
- LINE Bot。
- 使用者帳號系統。
- 自行保存使用者對話。
- 自動報案。
- 產生詐騙話術或攻擊流程。

## 4. 專案架構

```text
anti-scam-ai-knowledge-tw/
├── README.md
├── DEVELOPMENT.md
├── AGENTS.md
├── SECURITY.md
├── PRIVACY.md
├── requirements.txt
├── pyproject.toml
├── config/
│   └── sources.json
├── data/
│   ├── raw/
│   ├── processed/
│   └── archive/
├── knowledge/
│   ├── anti-scam-latest.md
│   ├── scam-patterns.md
│   ├── suspicious-domains.md
│   ├── report-guide.md
│   └── anti-scam-agent-prompt.md
├── scripts/
│   ├── fetch_165_open_data.py
│   ├── normalize_domains.py
│   ├── generate_markdown.py
│   ├── validate_output.py
│   └── update_all.py
├── docs/
│   ├── data-sources.md
│   ├── architecture.md
│   ├── roadmap.md
│   └── release-checklist.md
└── .github/
    └── workflows/
        └── update-knowledge.yml
```

## 5. 資料流程

```text
GitHub Actions / 手動執行
        ↓
scripts/update_all.py
        ↓
fetch_165_open_data.py：下載官方 CSV
        ↓
normalize_domains.py：欄位清理、URL/domain 正規化、去重
        ↓
generate_markdown.py：產生 AI 可讀 Markdown
        ↓
validate_output.py：檢查輸出檔案、筆數、欄位、日期
        ↓
commit 到 GitHub repo
```

## 6. 輸出檔案規格

### `data/processed/scam-domains.csv`

欄位建議：

| 欄位 | 說明 |
|---|---|
| `year_month_roc` | 民國年月，保留原始資料格式 |
| `domain` | 正規化後網域 |
| `raw_domain` | 原始網域或網址 |
| `site_type` | 官方資料中的網站性質 |
| `legal_basis` | 官方資料中的法律依據 |
| `requesting_agency` | 聲請單位 |
| `source` | 資料來源 |
| `updated_at` | 本專案處理時間 |

### `data/processed/scam-domains.json`

```json
{
  "metadata": {
    "generated_at": "2026-06-06T00:00:00+08:00",
    "source": "https://data.gov.tw/dataset/176455",
    "record_count": 0
  },
  "records": [
    {
      "domain": "example.com",
      "raw_domain": "https://example.com/path",
      "site_type": "涉詐網站",
      "legal_basis": "原始資料法律依據",
      "requesting_agency": "原始資料聲請單位"
    }
  ]
}
```

### `knowledge/anti-scam-latest.md`

固定包含：

1. 更新時間。
2. 資料來源。
3. 使用規則。
4. 高風險特徵。
5. 常見詐騙類型。
6. 官方查證建議。
7. 涉詐網站統計摘要。
8. AI 回答格式。
9. 安全限制。

## 7. 安全規則

AI Agent 必須遵守：

1. 只協助識詐、防詐、查證、保存證據、諮詢與報案。
2. 不產生可用於詐騙的完整話術。
3. 不優化詐騙流程。
4. 不提供規避平台偵測、封鎖、警方追查的方法。
5. 不要求使用者提供完整身分證字號、銀行帳號密碼、驗證碼、信用卡完整卡號。
6. 不把 AI 判斷當成法律或警方判定。
7. 資訊不足時輸出「無法判定」。

## 8. AI 回答格式

建議所有使用者分析結果都用下列格式：

```markdown
## 風險判斷

風險等級：低 / 中 / 高 / 極高 / 無法判定
可能詐騙類型：假投資 / 假網拍 / 假客服 / 解除分期付款 / 釣魚網站 / 其他

## 可疑特徵

- 特徵 1
- 特徵 2
- 特徵 3

## 查證步驟

1. 不點擊陌生連結。
2. 不提供驗證碼、密碼或金融資料。
3. 使用官方 App、官方網站或客服電話查證。
4. 必要時撥打 165 諮詢。

## 若已造成財損

- 保存對話、電話、網址、轉帳紀錄與帳戶資料。
- 儘速聯絡銀行止付或凍結。
- 前往派出所報案。

## 不確定事項

- 仍需要哪些資訊才能進一步判斷。
```

## 9. 開發里程碑

### v0.1.0：Markdown 知識包

- 完成資料來源設定。
- 完成 CSV 讀取與正規化。
- 完成 Markdown 產生。
- 完成 GitHub Actions。

### v0.2.0：RAG 格式支援

- 產生 chunked JSONL。
- 提供 LangChain / LlamaIndex 範例。
- 提供 Open WebUI 匯入說明。

### v0.3.0：CLI 工具

- 提供 `anti-scam-ai-pack update`。
- 提供 `anti-scam-ai-pack check-domain example.com`。

### v0.4.0：n8n Workflow

- 提供 n8n 範例流程。
- 可定期拉取更新並通知使用者。

### v1.0.0：穩定版

- 資料來源穩定。
- 測試完整。
- 文件完整。
- 安全規則完整。

## 10. Codex / Claude Code 開發指令

可將以下內容貼給 Codex：

```text
請根據 DEVELOPMENT.md、AGENTS.md、SECURITY.md，完成 anti-scam-ai-knowledge-tw 專案第一版。請先建立 Python 腳本、資料處理流程、Markdown 產生器與 GitHub Actions。不得加入任何收集使用者對話、保存個資、產生詐騙話術或規避偵測的功能。
```
