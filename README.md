# 🛡️ Anti-Scam AI Knowledge TW (台灣防詐騙 AI 知識包)

[![Update Anti-Scam Knowledge](https://github.com/your-username/anti-scam-ai-knowledge-tw/actions/workflows/update-knowledge.yml/badge.svg)](https://github.com/your-username/anti-scam-ai-knowledge-tw/actions/workflows/update-knowledge.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

本專案旨在提供一個 **自動更新、開源、且專為 AI 讀取設計的台灣防詐騙知識庫**。

透過 Python 自動化腳本，本專案每日從**內政部警政署 165 全民防騙網、165 打詐儀錶板、以及政府資料開放平臺**抓取最新的涉詐網站清單、真實詐騙案例、最新闢謠公告與打詐統計數據，並將其整理為 AI / LLM 能直接高效率讀取的結構化 Markdown 檔案。

> ⚠️ **專案重要聲明**：本專案僅提供「識詐、防詐、查證、保存證據、諮詢與報案建議」的知識。**本專案絕不收集任何使用者對話隱私，亦不提供任何可能被用於詐騙之話術生成或洗錢规避技術。**

---

## 📂 專案結構與產出檔案

```text
anti-scam-ai-knowledge-tw/
├── README.md                          # 專案中文使用說明書
├── AGENTS.md                          # 專為 AI 代理程式 (Cursor, Claude Code) 設計的引導規範
├── requirements.txt                   # Python 依賴清單
├── .github/workflows/
│   └── update-knowledge.yml           # GitHub Actions 每日自動更新排程
├── config/
│   └── sources.json                   # 資料來源設定檔
├── data/
│   ├── raw/                           # 抓取到的原始資料 (CSV, JSON)
│   └── processed/
│       ├── scam-domains.csv           # 整理後去重且正規化之涉詐網域清單 (CSV)
│       ├── scam-domains.json          # 整理後之涉詐網域 JSON (適合 RAG / API)
│       ├── rumors.csv                 # 整理後的闢謠公告清單 (CSV)
│       └── rumors.json                # 整理後的闢謠公告 JSON
└── knowledge/
    ├── anti-scam-latest.md            # 【核心】最新防詐騙 AI 知識包 (定期更新數據、案例與話術)
    ├── suspicious-domains.md          # 涉詐網站封鎖範例清單
    ├── scam-patterns.md               # 四大常見詐騙手法之特徵與話術拆解
    ├── report-guide.md                # 報案、諮詢、檢舉緊急處置指南
    └── anti-scam-agent-prompt.md      # 防詐 AI Agent 專用 System Prompt 提示詞
```

---

## 🚀 快速開始 (Quick Start)

如果你想在本地端執行更新腳本或取得最新資料：

### 1. 安裝環境與依賴

確認你的系統已安裝 Python 3.8+：

```bash
# 複製專案
git clone https://github.com/<your-username>/anti-scam-ai-knowledge-tw.git
cd anti-scam-ai-knowledge-tw

# 建立並啟用虛擬環境
python -m venv .venv
source .venv/bin/activate  # Windows 請執行: .venv\Scripts\activate

# 安裝 Python 套件
pip install -r requirements.txt
```

### 2. 執行手動更新

```bash
python scripts/update_all.py
```

執行後，腳本會自動：
1. 查詢政府開放資料 API，下載最新的 `涉詐網站清單` 與 `闢謠專區` 資料。
2. 連線 `165打詐儀錶板` API，抓取今日最新詐騙統計、最氾濫手法、警政署警訊以及最新真實案例。
3. 進行網域正規化與重複資料清理。
4. 在 `knowledge/` 目錄下重新生成所有的 Markdown 知識包。
5. 進行生成檔案驗證。

---

## 🤖 AI 使用者操作指引 (How to Use with AI)

本知識包提供兩種主要方式讓一般使用者或開發者匯入 AI 中使用：

### 方式 1：直接餵給 ChatGPT / Claude / Gemini (對話框直接讀取)

如果你是在網頁端使用 ChatGPT、Claude 或 Gemini，希望 AI 幫你判斷一封簡訊或一個網站是否為詐騙：

1. **下載知識包**：
   下載本專案中的 [knowledge/anti-scam-latest.md](file:///home/kali/Desktop/165_knowledge/anti-scam-ai-knowledge-tw/knowledge/anti-scam-latest.md) 檔案。
2. **上傳給 AI**：
   將該檔案作為附件上傳至聊天對話框中。
3. **輸入提示詞**：
   對 AI 複製並發送以下引導詞：
   ```text
   請讀取這份防詐騙知識包。
   接下來我會貼上可疑簡訊、LINE 對話截圖文字、廣告話術或網址。
   請根據這份資料與內附的安全規則幫我判斷風險等級、列出可疑特徵，並提供我具體的查證或緊急處置步驟。
   ```
4. **開始查證**：
   接下來你可以將任何可疑的訊息或網址貼給 AI 進行分析。

---

### 方式 2：給 Codex / Claude Code / Cursor / Windsurf 專案讀取

如果你正在使用 AI 輔助開發工具（如 Cursor, Claude Code, Copilot），希望 AI 助手在你的專案開發過程中隨時擁有防詐常識與安全規範：

1. 將本專案中的下列兩個核心檔案放置在你的專案根目錄或 RAG 檢索資料夾中：
   * `AGENTS.md` (或複製其內容至專案說明文檔中)
   * `knowledge/anti-scam-latest.md` (或整個 `knowledge/` 目錄)
2. 在 Cursor 中，你可以使用 `@AGENTS.md` 與 `@anti-scam-latest.md` 來讓 AI 對話時參考。
3. 如果是使用 Claude Code，它會自動讀取根目錄下的 `AGENTS.md` 作為 Agent 的行為準則，確保開發時編寫的程式碼自動遵守台灣防詐法規與安全限制。

---

## 📊 資料來源與引用規範

本專案使用之所有資料皆為政府公開資訊或官方公開平台：
1. **政府資料開放平臺**：
   * [165反詐專線_遭停止解析涉詐網站](https://data.gov.tw/dataset/176455) (內政部警政署刑事警察局提供，依據《詐欺犯罪危害防制條例》第42條辦理)
   * [165反詐騙諮詢專線－詐騙闢謠專區](https://data.gov.tw/dataset/38262) (內政部警政署提供)
2. **內政部警政署 165 全民防騙網**：[https://165.npa.gov.tw/](https://165.npa.gov.tw/)
3. **內政部警政署 165 打詐儀錶板**：[https://165dashboard.tw/](https://165dashboard.tw/)

---

## 🛠️ GitHub Actions 自動更新設定

本專案預設已配置 GitHub Actions 每日於台北時間上午 9:00 (01:00 UTC) 自動執行更新並推送 (Push) 最新 Markdown 到您的 Repo。

### 設定步驟：
1. 將此專案 Fork 到您自己的 GitHub 帳號下。
2. 進入 Repo 的 **Settings -> Actions -> General**，確保 **Workflow permissions** 設置為 **Read and write permissions** (因為 Actions 需要將更新後的知識包 push 回 repo)。
3. *(選用)* 如果您有特定的代理下載網址，可以在 **Settings -> Secrets and variables -> Actions** 中添加名為 `ANTI_SCAM_CSV_URL` 的 Secret，否則專案會自動動態解析 data.gov.tw 的最新 CSV 下載網址。

---

## ⚖️ 授權與隱私說明 (License & Privacy)

* 本專案代碼採用 **MIT License** 授權開源。
* 數據資料來源屬於中華民國政府公務機關公開資料，使用時請遵循政府資料開放授權條款及相關引用規範。
* **隱私聲明**：本工具純屬本地端靜態知識庫整理，不包含任何網路對話記錄器，絕不收集、處理或上傳使用者的任何私密聊天對話或個人帳密資訊。
