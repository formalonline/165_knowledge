"""Generate AI-readable Markdown files from processed data and raw APIs."""
from __future__ import annotations

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

import pandas as pd

TZ_TAIPEI = timezone(timedelta(hours=8))


def now_text() -> str:
    return datetime.now(TZ_TAIPEI).strftime("%Y-%m-%d %H:%M:%S %z")


def read_json_safe(path: Path) -> dict | list:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def generate_suspicious_domains(processed_csv: Path, out_dir: Path) -> None:
    if not processed_csv.exists():
        print("Warning: Processed domains CSV not found. Skipping suspicious-domains.md generation.")
        return

    df = pd.read_csv(processed_csv, dtype=str, encoding="utf-8-sig")
    sample = df.head(100)
    lines = [
        "# 涉詐網站資料摘要",
        "",
        f"更新時間：{now_text()}",
        "",
        "資料來源：政府資料開放平臺 165反詐騙諮詢專線_遭停止解析涉詐網站",
        "",
        f"目前攔阻解析總網域筆數：{len(df)} 筆",
        "",
        "## 使用提醒",
        "",
        "此清單為台灣警政機關予以停止解析的涉詐網域。未出現在清單中不代表一定安全；已在清單中的網域，AI 應直接判定為高風險詐騙網站。",
        "",
        "## 攔阻網域範例（最新處理隨機抽樣 100 筆）",
        "",
    ]
    for _, row in sample.iterrows():
        domain = row.get("domain", "")
        site_type = row.get("site_type", "涉詐網站")
        if domain:
            lines.append(f"- `{domain}` ({site_type})")
    (out_dir / "suspicious-domains.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def generate_agent_prompt(out_dir: Path) -> None:
    content = """# 防詐騙 AI Agent 提示詞 (AGENTS.md / System Prompt)

你是台灣防詐騙 AI 助手 (Taiwan Anti-Scam AI Assistant)。你的任務是協助使用者辨識可疑簡訊、LINE 對話、社群廣告、電話話術、投資連結、購物網站與 QR Code 內容。

## 核心行為守則 (Core Guardrails)
1. **只做防詐與識詐**：只提供識詐、防詐、查證、保存證據、諮詢與報案建議。
2. **絕不生成詐騙內容**：不得產生可用於詐騙的完整話術、劇本，或優化詐騙流程。
3. **絕不提供逃避追查方法**：不得提供規避平台偵測、警方追查、洗錢或逃避法律制裁的方法。
4. **個資保護**：若使用者提供敏感個資（完整身分證、銀行帳密、驗證碼、信用卡號等），必須發出安全警示並要求使用者立刻遮蔽或刪除，不得記錄或重複輸出。
5. **非法律或司法判定**：AI 判斷僅供風險參考，不具法律效力。若不確定，請輸出「無法判定」並建議使用者撥打 165 諮詢。

## 判斷邏輯
1. **網址/網域比對**：若使用者貼上的網址出現在涉詐網站清單中，直接判定為「極高風險（已由警方攔阻）」。
2. **話術/情境特徵比對**：對照常見的假投資、假網拍、假檢警、假客服特徵進行風險評估。
3. **查證引導**：提供具體查證步驟，例如使用官方 App 聯絡客服，或撥打 165 專線。

## 建議輸出格式 (Must Follow Output Format)

```markdown
## 風險判斷

- **風險等級**：低 / 中 / 高 / 極高 / 無法判定
- **可能詐騙類型**：假投資 / 假網拍 / 假客服 / 解除分期付款 / 網路交友 / 假檢警 / 釣魚網站 / 其他
- **判斷依據**：比對官方涉詐網站清單、最新公告案例與高風險特徵

## 可疑特徵

- [說明具體可疑之處，例如：使用簡體字、網址非官方、承諾高回報、製造急迫感等]

## 建議查證步驟

1. [步驟 1，例如：不要點擊連結]
2. [步驟 2，例如：透過官方專線或 APP 查證]
3. [步驟 3，例如：有任何疑慮，請撥打 165 反詐騙諮詢專線]

## 若已造成財損（匯款或提供帳密卡號）

1. **保存證據**：完整截圖對話、轉帳明細、網址與電話號碼。
2. **聯絡銀行**：如剛匯款，立即聯絡銀行進行「圈存」止付。
3. **報案登記**：撥打 165 登記並儘速至附近派出所製作筆錄。

## 不確定事項 / 需要補充資訊

- [若有資訊不足之處在此列出]
```
""".strip()
    (out_dir / "anti-scam-agent-prompt.md").write_text(content + "\n", encoding="utf-8")


def generate_latest(processed_json: Path, raw_dir: Path, out_dir: Path) -> None:
    # Read normalized domains
    payload_domains = read_json_safe(processed_json)
    if isinstance(payload_domains, dict):
        record_count = payload_domains.get("metadata", {}).get("record_count", 0)
    else:
        record_count = 0

    # Read normalized rumors
    payload_rumors = read_json_safe(processed_json.parent / "rumors.json")
    rumors_list = payload_rumors.get("records", []) if isinstance(payload_rumors, dict) else []

    # Read 165 Dashboard API files
    dashboard_ranking = read_json_safe(raw_dir / "dashboard_ranking.json")
    today_methods = read_json_safe(raw_dir / "today_fraud_methods.json")
    news_ticker = read_json_safe(raw_dir / "news_ticker.json")
    daily_cases = read_json_safe(raw_dir / "daily_cases.json")

    # Start constructing anti-scam-latest.md
    lines = [
        "# 台灣防詐騙 AI 知識包 (Anti-Scam AI Knowledge Pack)",
        "",
        f"**最後更新時間**：{now_text()}",
        "**資料來源**：內政部警政署 165 全民防騙網、165 打詐儀錶板、政府資料開放平臺",
        f"**涉詐封鎖網站總數**：{record_count} 筆",
        "",
        "---",
        "",
        "## 📊 165 打詐儀錶板：今日最新數據與趨勢",
        "",
    ]

    # Parse dashboard ranking
    ranking_body = dashboard_ranking.get("body", {}) if isinstance(dashboard_ranking, dict) else {}
    if ranking_body:
        stats_date = ranking_body.get("Date", "")
        if stats_date:
            try:
                # Convert ISO timestamp to readable date
                dt = datetime.fromisoformat(stats_date.replace("Z", "+00:00"))
                stats_date = dt.astimezone(TZ_TAIPEI).strftime("%Y-%m-%d")
            except Exception:
                pass
        total_cases = ranking_body.get("TotalCases", 0)
        total_losses = ranking_body.get("TotalLosses", 0.0)

        lines.extend([
            f"- **數據統計日期**：{stats_date}",
            f"- **單日通報總件數**：{total_cases} 件",
            f"- **單日通報財損金額**：{total_losses:,.1f} 萬元 (新台幣)",
            "",
            "### 當日通報詐騙手法前五名 (Top 5 Scam Methods)",
            "",
            "| 排名 | 詐騙手法名稱 | 通報件數 | 財損金額 (萬元) |",
            "|---|---|---|---|",
        ])

        top_five = ranking_body.get("TopFive", [])
        if top_five:
            for idx, item in enumerate(top_five, 1):
                lines.append(
                    f"| {idx} | {item.get('Name', '')} | {item.get('Cases', 0)} | {item.get('Losses', 0.0):,.1f} |"
                )
        else:
            lines.append("| - | 無資料 | - | - |")
        lines.append("")
    else:
        lines.append("*(暫無今日打詐儀錶板統計數據)*\n")

    # Parse News Ticker marquee warnings
    lines.append("## 📢 警政署最新防詐警訊")
    lines.append("")
    ticker_body = news_ticker.get("body", []) if isinstance(news_ticker, dict) else []
    if isinstance(ticker_body, list) and ticker_body:
        for item in ticker_body[:6]:
            title = item.get("NewsTickerTitle", "").strip()
            if title:
                lines.append(f"- ⚠️ **警示**：{title}")
        lines.append("")
    else:
        lines.append("*(暫無最新公告警訊)*\n")

    # Parse Real Cases Study List
    lines.append("## 🔍 最新真實詐騙案例拆解")
    lines.append("")
    cases_body = daily_cases.get("body", []) if isinstance(daily_cases, dict) else []
    if isinstance(cases_body, list) and cases_body:
        for idx, item in enumerate(cases_body[:5], 1):
            title = item.get("CaseTitle", "").strip()
            content = item.get("CaseContent", "").strip()
            # Replace double newlines with single p tag or spacing
            content = content.replace("\n", " ").strip()
            if len(content) > 300:
                content = content[:300] + "..."
            if title:
                lines.extend([
                    f"### 案例 {idx}：{title}",
                    "",
                    f"> {content}",
                    "",
                ])
    else:
        lines.append("*(暫無最新真實案例資料)*\n")

    # Parse Today Fraud Methods Descriptions
    lines.append("## 💡 常見詐騙手法與話術解析")
    lines.append("")
    methods_body = today_methods.get("body", []) if isinstance(today_methods, dict) else []
    if isinstance(methods_body, list) and methods_body:
        for item in methods_body:
            name = item.get("Name", "").strip()
            desc = item.get("Description", "").strip()
            if name and desc:
                # Format bullet points nicely
                formatted_desc = desc.replace("\n", "\n- ")
                lines.extend([
                    f"### 🛑 {name}",
                    "",
                    f"- {formatted_desc}",
                    "",
                ])
    else:
        lines.append("*(暫無詳細話術解析資料)*\n")

    # Parse Rumors / Clarifications
    lines.append("## 🛡️ 官方闢謠與澄清澄清專區")
    lines.append("")
    if rumors_list:
        for item in rumors_list[:5]:
            title = item.get("title", "").strip()
            content = item.get("content", "").strip()
            pub_time = item.get("publish_time", "").strip()
            if title:
                # Limit content length
                if len(content) > 250:
                    content = content[:250] + "..."
                lines.extend([
                    f"### 📌 {title} ({pub_time})",
                    "",
                    f"{content}",
                    "",
                ])
    else:
        lines.append("*(暫無闢謠專區資料)*\n")

    # Static High-Risk Features & Rules
    lines.extend([
        "## 🚫 常用高風險特徵 (Red Flags)",
        "",
        "1. **高回報承諾**：宣稱「穩賺不賠」、「保證獲利」、「高息理財」、「內線布局」。",
        "2. **加 LINE 私聊**：廣告、網拍客服要求「加 LINE 私下交易或諮詢」以規避平台監控。",
        "3. **非官方客服連結**：提供假冒銀行、郵局、蝦皮、淘寶的簡訊或網址，要求登入或操作。",
        "4. **要求輸入機密金流資訊**：索取「信用卡驗證碼」、「手機簡訊認證碼」、「網銀帳號密碼」。",
        "5. **操作 ATM/無卡提款**：誆稱「解除分期付款設定」、「扣款錯誤」、「會員身分錯誤」。",
        "6. **匯款到私人帳戶**：要求轉帳到不相干的個人銀行帳戶，或透過加密貨幣錢包轉帳。",
        "",
        "## 🛡️ 官方查證建議步驟",
        "",
        "- **不點擊**：收到陌生簡訊或電子郵件的縮網址、連結，絕對不點選。",
        "- **不操作**：任何公務機關或電商平台，絕對不會要求民眾操作 ATM、網銀或無卡提款進行「解除錯誤」。",
        "- **認明官方網域**：台灣政府機關網址結尾必為 `.gov.tw`，學校必為 `.edu.tw`，公司官方多有獨特網域，請勿信 `line-helper-vip.xyz` 等怪異網域。",
        "- **撥打 165**：若有任何疑慮，請立即撥打 **165反詐騙諮詢專線** 或至 **165 全民防騙網** 求證。",
        "",
        "## 🤖 AI Agent 任務指引與安全限制",
        "",
        "1. **限制**：只協助識詐、防詐、查證、保存證據、諮詢與報案。不得提供任何可被用於詐騙的劇本、話術生成或洗錢指引。",
        "2. **不重複個資**：若使用者輸入完整金融卡號、帳密、身分證字號、簡訊驗證碼，請警告使用者遮蔽，並不得在 AI 的回覆中重複輸出該機密資訊。",
        "3. **免責聲明**：回答末尾須提醒「AI 判斷僅供參考，若遇緊急狀況或財損，請立刻撥打 165 諮詢或 110 報案」。",
    ])

    (out_dir / "anti-scam-latest.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def generate_static_guides(out_dir: Path) -> None:
    report = """# 報案、諮詢、檢舉建議步驟

當您遇到詐騙或疑似詐騙事件時，請依照下列步驟處理，以保護財產安全並協助警方打擊犯罪：

## 1. 尚未造成財物損失時（預防階段）
*   **停止互動**：立刻終止與可疑帳號（LINE 網友、投資老師、假客服）的聯絡。
*   **截圖保存**：截圖保留對話內容、對方頭像、提供的投資網站網址、使用的匯款帳號及電話號碼。
*   **查證確認**：
    *   撥打 **165反詐騙專線** 諮詢。
    *   利用本知識包比對涉詐網站清單。
    *   在 **165 全民防騙網** 進行涉詐網址/電話/LINE ID 檢索。

## 2. 已匯款、轉帳或交付現金時（緊急止付階段）
*   **緊急圈存（10分鐘內黃金期）**：
    1.  立刻撥打 **165** 專線，提供**轉出帳戶、轉入帳戶、轉帳金額與精確時間**。
    2.  165 聯絡銀行進行「緊急圈存」，將對方帳戶暫時凍結 24 小時。
    3.  圈存成功後，您必須在 **24 小時內** 帶着相關轉帳證明，前往最近的派出所報案，正式完成列為「警示帳戶」手續。
*   **直接聯繫銀行**：您也可以直接聯絡您轉出銀行的客服，申請對該筆交易進行凍結或止付。

## 3. 前往派出所報案準備資料
前往派出所報案時，請攜帶以下資料，能加快警方案件登錄與偵辦速度：
*   **身分證明文件**：身分證。
*   **交易明細證明**：網銀轉帳成功畫面（須含交易序號）、ATM交易明細表、臨櫃匯款單或現金交付收據。
*   **通訊紀錄截圖**：對話對策、投資群組對話、誘導匯款的文字、對方提供的網址截圖。
*   **詐欺網址或帳號資訊**：對方的 LINE ID、電話、詐騙平台網址。

## 4. 平台檢舉
*   **LINE**：在聊天室選單點選「檢舉」，類別選擇「傳送垃圾訊息」或「其他」。
*   **Facebook / Instagram**：在該廣告或粉專點選「檢舉」，選擇「詐騙或虛假資訊」。
*   **Google 廣告**：前往 Google 廣告檢舉頁面，檢舉惡意釣魚廣告。
""".strip()

    patterns = """# 常見詐騙手法與特徵 (Scam Patterns)

以下整理台灣地區最氾濫的四類詐騙手法、其核心特徵與常見話術，協助 AI 進行精準判斷：

## 1. 假投資理財詐騙 (極高財損)
*   **核心話術**：
    *   「老師帶路、內線消息、穩賺不賠、保證獲利」
    *   「加入 VIP 飆股交流群，領取免費明牌」
    *   「使用特定理財 App/平台交易，出金需要聯絡客服」
    *   「出金要先繳 20% 稅金、保證金或渠道服務費」
*   **可疑行為**：
    *   要求下載非 Google Play / App Store 官方商店的第三方 App (例如透過網址點擊安裝 IPA/APK)。
    *   要求將資金匯入「個人銀行帳戶」或私下購買加密貨幣轉至特定錢包。

## 2. 假網拍與一頁式廣告詐騙
*   **核心話術**：
    *   「限時特惠、工廠清倉、倒閉出清、貨到付款免運費」
    *   「假冒股市名人或知名品牌特賣會（如LV、Dyson特價）」
*   **可疑行為**：
    *   商品價格遠低於市價（如最新 iPhone 僅售數千元）。
    *   一頁式網站結構粗糙，包含大量簡體字、倒數計時器、虛假好評，且「無公司地址、無聯絡電話」。
    *   客服聯絡方式僅能加 LINE。

## 3. 解除分期付款與假客服詐騙
*   **核心話術**：
    *   「您之前在我們平台購買的訂單被重複扣款，或是被設為批發商/VIP會員」
    *   「系統扣款出錯，需要引導您操作 ATM 或網路銀行進行身分驗證、解除設定」
    *   「金流異常，帳戶面臨凍結，需轉帳到安全帳戶進行信託認證」
*   **可疑行為**：
    *   來電顯示開頭為 `+` 號（例如 `+886...` 且後面為一般市話，多為境外竄改來電）。
    *   要求使用者前往 ATM 或打開網銀轉帳。

## 4. 網路交友與假檢警詐騙
*   **核心話術**：
    *   「親愛的，我寄給你的禮物被海關扣留，需要繳交關稅或解凍費才能領取」
    *   「我是檢察官/警察，你的涉嫌洗錢案，帳戶需要接受監管，請把錢轉到監管帳戶」
*   **可疑行為**：
    *   公務機關或檢警絕對不會在電話中製作筆錄，更不會要求「監管帳戶」或「交付現金給公證人」。
""".strip()

    (out_dir / "report-guide.md").write_text(report + "\n", encoding="utf-8")
    (out_dir / "scam-patterns.md").write_text(patterns + "\n", encoding="utf-8")


def generate_all_markdown(processed_csv: Path, processed_json: Path, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    generate_suspicious_domains(processed_csv, out_dir)
    generate_latest(processed_json, processed_csv.parents[2] / "data" / "raw", out_dir)
    generate_agent_prompt(out_dir)
    generate_static_guides(out_dir)
    print(f"Generated Markdown files in {out_dir}")
