#!/bin/bash
#
# AIOps 系統日誌分析腳本 (AIOps System Log Analysis Script)
#
# 功能：
# 1. 蒐集過去一小時內 Apache 的錯誤日誌 (404, 500, 503)。
# 2. 蒐集當前 MySQL/MariaDB 的 `SHOW FULL PROCESSLIST` 狀態。
# 3. 使用 Gemini CLI (非互動模式) 分析上述資料。
# 4. 將分析報告儲存至 /var/log/report/。
#
# 作者：Gemini
# 版本：1.0
# 日期：2025-09-21

set -e # 若指令失敗則立即退出
set -o pipefail # 確保管道命令的返回碼正確

# --- 組態設定 (請根據您的環境修改) ---

# 1. Gemini API Key
# !! 重要：請勿將 API Key 直接寫在此處。請使用環境變數設定。
# !! 執行前請先 export GEMINI_API_KEY="您的API_KEY"
if [ -z "${GEMINI_API_KEY}" ]; then
    echo "[錯誤] 環境變數 GEMINI_API_KEY 未設定。"
    echo "請執行 export GEMINI_API_KEY='您的API金鑰' 後再試一次。"
    exit 1
fi

# 2. MySQL/MariaDB 連線資訊
# 建議使用 ~/.my.cnf 設定檔來存放認證資訊，以策安全。
# 若使用設定檔，以下變數可留空。
DB_USER=""
DB_PASS=""
DB_HOST="localhost"

# 3. 日誌與報告路徑
APACHE_LOG_DIR="/var/log/LMS_LOG"
REPORT_DIR="/var/log/report"
ARCHIVE_DIR="${REPORT_DIR}/archive"

# 4. 暫存檔案
TEMP_DATA_FILE=$(mktemp)
PROMPT_FILE=$(mktemp)

# --- 腳本主體 ---

echo "=== AIOps 系統健康度分析腳本啟動 @ $(date '+%Y-%m-%d %H:%M:%S') ==="

# 步驟 1: 建立報告目錄
echo "[1/5] 檢查並建立報告目錄..."
mkdir -p "${REPORT_DIR}"
mkdir -p "${ARCHIVE_DIR}"
echo "報告目錄: ${REPORT_DIR}"

# 步驟 2: 蒐集 Apache 錯誤日誌
echo "[2/5] 正在蒐集最近一小時的 Apache 錯誤日誌..."
# 使用 find 找出過去 60 分鐘內有修改過的 access_log 檔案
# 再用 grep 過濾出包含 404, 500, 503 狀態碼的日誌行
APACHE_ERRORS=$(find "${APACHE_LOG_DIR}" -name "*access_log*" -mmin -60 -type f -print0 | xargs -0 grep -E ' (404|500|503) ' || echo "沒有發現 Apache 錯誤日誌。")
echo "Apache 日誌蒐集完成。"

# 步驟 3: 蒐集 MySQL Process List
echo "[3/5] 正在蒐集 MySQL/MariaDB Process List..."
# 優先使用 mysql 指令，如果失敗則嘗試 mariadb
MYSQL_COMMAND="mysql"
if ! command -v ${MYSQL_COMMAND} &> /dev/null; then
    MYSQL_COMMAND="mariadb"
    if ! command -v ${MYSQL_COMMAND} &> /dev/null; then
        echo "[錯誤] 找不到 mysql 或 mariadb 指令。"
        exit 1
    fi
fi

# 構建資料庫連線參數，優先使用 .my.cnf
MYSQL_OPTS=""
if [ -n "${DB_USER}" ]; then
    MYSQL_OPTS="--user=${DB_USER}"
fi
if [ -n "${DB_PASS}" ]; then
    MYSQL_OPTS="${MYSQL_OPTS} --password=${DB_PASS}"
fi
if [ -n "${DB_HOST}" ]; then
    MYSQL_OPTS="${MYSQL_OPTS} --host=${DB_HOST}"
fi

PROCESS_LIST=$(${MYSQL_COMMAND} ${MYSQL_OPTS} -e "SHOW FULL PROCESSLIST;" 2>/dev/null || echo "無法取得 MySQL Process List。請檢查連線設定或 .my.cnf 檔案。")
echo "MySQL Process List 蒐集完成。"

# 步驟 4: 組合資料並建立 Gemini 提示
echo "[4/5] 正在建構 Gemini 分析提示..."

# 將日誌與 Process List 寫入暫存檔
cat << DATA > "${TEMP_DATA_FILE}"
--- Apache 最近一小時錯誤日誌 (HTTP 404, 500, 503) ---
${APACHE_ERRORS}

--- 當前 MySQL/MariaDB Process List ---
${PROCESS_LIST}
DATA

# 建立給 Gemini 的提示檔案
cat << PROMPT > "${PROMPT_FILE}"
你是一位資深的 AIOps 網站可靠性工程師 (SRE)，專長是從日誌和系統狀態數據中快速找出潛在風險。

我將提供一份包含「過去一小時內 Apache 的錯誤日誌」和「當前的 MySQL/MariaDB Process List」的原始數據。

請依據這些數據，提供一份簡潔、專業的系統健康分析報告。報告需包含以下四個部分：

1.  **Apache 錯誤日誌分析**：
    * 總結主要的錯誤類型 (404, 500, 503) 分布情況。
    * 是否有特定 URL 或模式的錯誤頻繁出現？

2.  **潛在異常 IP 分析**：
    * 根據日誌中的 IP 位址，列出前 3-5 個最可疑的 IP。
    * 簡述每個可疑 IP 的行為特徵（例如：高頻率 404 掃描、觸發 500 錯誤等）。

3.  **MySQL 運行狀態分析**：
    * Process List 中是否有長時間運行的查詢 (long-running queries)？
    * 是否有鎖定 (locked) 或等待中的連線？
    * 連線來源 (Host) 是否有異常？

4.  **綜合評估與建議**：
    * 基於以上分析，對系統目前的健康狀況給出一個總體評價（例如：健康、輕微異常、需要關注、緊急）。
    * 提出 1-2 條最優先的處理建議。

現在，請開始分析以下提供的數據：
PROMPT

echo "提示建構完成。"

# 步驟 5: 執行 Gemini CLI 進行分析並產生報告
echo "[5/5] 正在呼叫 Gemini CLI 進行分析，請稍候..."

# 報告檔案名稱
REPORT_TIMESTAMP=$(date '+%Y%m%d-%H%M%S')
REPORT_FILE="${ARCHIVE_DIR}/system-analysis-${REPORT_TIMESTAMP}.txt"
LATEST_REPORT_LINK="${REPORT_DIR}/latest-report.txt"

# 執行 Gemini CLI，將提示檔案與資料檔案的內容結合後傳入
# 使用 'gemini' 作為指令，請確保它在您的 $PATH 中
(cat "${PROMPT_FILE}"; cat "${TEMP_DATA_FILE}") | gemini --api-key "${GEMINI_API_KEY}" > "${REPORT_FILE}"

if [ $? -eq 0 ]; then
    echo "分析報告已成功產生: ${REPORT_FILE}"
    # 更新 latest 連結
    ln -snf "${REPORT_FILE}" "${LATEST_REPORT_LINK}"
    echo "已更新最新報告連結: ${LATEST_REPORT_LINK}"
else
    echo "[錯誤] Gemini CLI 執行失敗。"
    # 如果失敗，保留暫存檔以供除錯
    echo "提示內容已保留在: ${PROMPT_FILE}"
    echo "原始數據已保留在: ${TEMP_DATA_FILE}"
    exit 1
fi

# 清理暫存檔
rm -f "${TEMP_DATA_FILE}" "${PROMPT_FILE}"

echo "=== 分析完成 ==="
