# MCP AI Agent 🤖

[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP Protocol](https://img.shields.io/badge/MCP-Protocol-green.svg)](https://modelcontextprotocol.io/)
[![Gemini SDK](https://img.shields.io/badge/Gemini-SDK-orange.svg)](https://ai.google.dev/)

一個基於 Google Gemini SDK 開發的智能 Linux 系統管理助手，採用 Model Context Protocol (MCP) 架構，提供安全、智能的系統自動化操作。結合人工智慧的自然語言理解與嚴格的安全控制機制，讓系統管理變得更簡單、更安全。

## 🎯 專案特色

### 🧠 核心技術架構

- **🔗 MCP AI Agent 基礎類**: 統一的 Gemini API 與 MCP 伺服器通信介面
- **⚙️ MCP 伺服器**: 將 Linux 系統操作封裝為標準化工具
- **🛡️ 多層安全機制**: 智能風險評估與操作確認系統
- **💻 非互動模式**: 完整的 CLI 命令列介面支援

### 🔍 智能系統監控助手

- **📊 自動監控**: 即時追蹤 CPU、記憶體、磁碟、網路等關鍵指標
- **🤖 AI 智能分析**: 基於機器學習的異常檢測與趨勢預測
- **⚡ 主動告警**: 智能問題發現與自動化解決方案推薦
- **🔧 高度可擴展**: 支援自定義監控規則與通知管道

### 🛠️ 自動化運維助手

- **💬 自然語言介面**: 使用日常語言描述即可執行複雜運維任務
- **🔒 安全執行**: 多層次安全檢查與智能風險評估
- **📋 標準化操作**: 降低人為錯誤，提升操作一致性
- **📝 完整審計**: 操作歷史記錄與一鍵回滾機制

## 📦 安裝指南

### 🔧 系統需求

- **作業系統**: Linux (Ubuntu 18.04+, CentOS 7+, Debian 10+)
- **Python**: 3.9 或以上版本
- **API 金鑰**: Google Gemini API Key
- **權限**: sudo 權限（用於系統操作）

### ⚡ 快速安裝

1. **下載專案**
```bash
git clone https://github.com/trionnemesis/mcp-ai-agent.git
cd mcp-ai-agent
```

2. **安裝依賴套件**
```bash
# 使用 pip 安裝
pip install -r requirements.txt

# 或使用開發模式安裝
pip install -e .
```

3. **設定環境變數**
```bash
# 複製環境變數範本
cp .env.example .env

# 編輯 .env 檔案，設定您的 Gemini API 金鑰
nano .env
```

4. **設定 Gemini API 金鑰**
```bash
export GEMINI_API_KEY="your_gemini_api_key_here"
```

5. **驗證安裝**
```bash
# 執行設定腳本
python setup_example.py

# 檢查系統狀態
mcp-agent status
```

## 🚀 使用指南

### 💻 命令列介面 (CLI)

#### 🔍 系統監控
```bash
# 開始無限期監控
mcp-agent monitor

# 監控指定時間（秒）
mcp-agent monitor --duration 3600

# 自定義監控閾值
mcp-agent monitor --cpu-threshold 90 --memory-threshold 80 --disk-threshold 95

# 詳細監控輸出
mcp-agent monitor --verbose
```

#### ⚙️ 系統操作
```bash
# 自然語言命令執行
mcp-agent execute "檢查系統狀態"
mcp-agent execute "重啟 nginx 服務"
mcp-agent execute "清理系統暫存檔案"

# 批次執行命令
mcp-agent execute --batch commands.txt

# 模擬模式（不實際執行）
mcp-agent execute "重啟伺服器" --dry-run

# 跳過確認提示
mcp-agent execute "檢查磁碟空間" --no-confirm
```

#### 🏥 系統健康檢查
```bash
# 快速健康檢查
mcp-agent health-check --quick

# 完整系統檢查
mcp-agent health-check

# JSON 格式輸出
mcp-agent health-check --format json
```

#### 🛠️ 工具管理
```bash
# 列出所有可用工具
mcp-agent tools-list

# 查看系統狀態
mcp-agent status

# 顯示版本資訊
mcp-agent version
```

### 🎮 互動式操作模式

```bash
# 啟動互動式助手
mcp-agent interactive
```

進入互動模式後，您可以使用自然語言與系統對話：

```
🔧 Operations> 檢查系統狀態
🧠 分析請求: 檢查系統狀態
✅ 操作完成時間 2.3 秒
📋 結果:
系統狀態良好：
- CPU 使用率: 25%
- 記憶體使用率: 68%
- 磁碟使用率: 45%
- 網路連線正常

🔧 Operations> 重啟 nginx 服務
⚠️ 這是一個中風險操作，是否繼續？ (y/N): y
🔄 正在重啟 nginx 服務...
✅ nginx 服務重啟成功

🔧 Operations> history
📜 操作歷史 (最近 10 項):
 1. ✅ 檢查系統狀態
    時間: 2.3s | 工具: get_system_info
 2. ✅ 重啟 nginx 服務
    時間: 5.1s | 工具: manage_service
```

## 🛠️ MCP 工具集詳解

### 📊 系統資訊收集工具

#### `get_system_info`
收集完整的系統資訊，包括 CPU、記憶體、磁碟使用情況。

```bash
# 基本系統資訊
mcp-agent execute "顯示系統資訊"

# 詳細系統資訊
mcp-agent execute "顯示詳細系統資訊包含負載平均和網路IO"
```

#### `monitor_processes`
進階進程監控與分析功能。

```bash
# 監控 CPU 使用率最高的進程
mcp-agent execute "顯示 CPU 使用率最高的 10 個進程"

# 根據進程名稱過濾
mcp-agent execute "顯示所有 python 相關進程"

# 記憶體使用量排序
mcp-agent execute "按記憶體使用量排序顯示進程"
```

### ⚙️ 系統服務管理工具

#### `manage_service`
systemd 服務的完整管理功能。

```bash
# 服務控制命令
mcp-agent execute "啟動 apache2 服務"
mcp-agent execute "停止 mysql 服務"
mcp-agent execute "重啟 nginx 服務"
mcp-agent execute "檢查 ssh 服務狀態"
mcp-agent execute "啟用 docker 服務開機自啟"
mcp-agent execute "停用 apache2 服務開機自啟"
```

### 📋 日誌分析工具

#### `check_logs`
強大的系統日誌查看與分析功能。

```bash
# 查看系統日誌
mcp-agent execute "顯示最近 100 行系統日誌"

# 特定服務日誌
mcp-agent execute "顯示 nginx 服務的日誌"

# 錯誤級別日誌
mcp-agent execute "顯示錯誤級別的系統日誌"

# 即時日誌監控
mcp-agent execute "即時監控 apache 服務日誌"
```

#### `log_analysis_tools`
進階日誌分析與模式識別。

```bash
# 錯誤分析
mcp-agent execute "分析系統日誌中的錯誤模式"

# 自定義模式搜尋
mcp-agent execute "在 nginx 日誌中搜尋 404 錯誤"

# 日誌摘要分析
mcp-agent execute "生成過去 24 小時的日誌摘要"
```

### 📁 檔案與目錄操作工具

#### `file_operations`
安全的檔案系統操作功能。

```bash
# 檔案管理
mcp-agent execute "列出 /var/log 目錄內容"
mcp-agent execute "建立 /tmp/backup 目錄"
mcp-agent execute "複製 /etc/nginx/nginx.conf 到 /tmp"
mcp-agent execute "設定 /var/www/html 權限為 755"

# 危險操作（需要確認）
mcp-agent execute "刪除 /tmp/old_files 目錄"
```

### 🌐 網路診斷工具

#### `network_diagnostics`
完整的網路連線診斷功能。

```bash
# 連線測試
mcp-agent execute "ping google.com 測試網路連線"
mcp-agent execute "追蹤到 8.8.8.8 的路由"

# 網路狀態檢查
mcp-agent execute "顯示所有網路介面資訊"
mcp-agent execute "顯示目前的網路連線狀態"
mcp-agent execute "檢查開放的網路埠"
```

### 💾 磁碟管理工具

#### `disk_management`
磁碟空間分析與管理功能。

```bash
# 磁碟使用分析
mcp-agent execute "檢查根目錄磁碟使用量"
mcp-agent execute "顯示所有磁碟分割區使用情況"
mcp-agent execute "分析 /var 目錄磁碟使用量"

# 大檔案搜尋
mcp-agent execute "尋找大於 100MB 的檔案"
```

### 🔒 安全審計工具

#### `security_audit_tools`
系統安全檢查與合規性評估。

```bash
# 基本安全檢查
mcp-agent execute "執行基本系統安全審計"

# 檔案權限審計
mcp-agent execute "檢查系統中的可寫檔案權限"

# 網路安全檢查
mcp-agent execute "審計網路安全設定"

# 使用者帳戶審計
mcp-agent execute "檢查系統使用者帳戶安全性"
```

### 💾 備份與恢復工具

#### `backup_and_recovery_tools`
系統備份與恢復管理。

```bash
# 建立備份
mcp-agent execute "備份 /etc 目錄到 /backup"
mcp-agent execute "使用 gzip 壓縮備份 /home/user"

# 備份驗證
mcp-agent execute "驗證 /backup/etc_backup.tar.gz 備份檔案"

# 備份列表
mcp-agent execute "列出 /backup 目錄中的所有備份"
```

### 🐳 容器管理工具

#### `container_management_tools`
Docker 容器管理功能。

```bash
# 容器操作
mcp-agent execute "列出所有 Docker 容器"
mcp-agent execute "顯示容器資源使用統計"
mcp-agent execute "檢查指定容器的日誌"
mcp-agent execute "清理未使用的 Docker 容器"
```

## ⚙️ 設定選項

### 🌍 環境變數設定

建立 `.env` 檔案或設定系統環境變數：

```bash
# Gemini API 設定
GEMINI_API_KEY=your_gemini_api_key_here    # 必要：Google Gemini API 金鑰
GEMINI_MODEL=gemini-1.5-pro                 # 選用：使用的 Gemini 模型

# MCP 伺服器設定
MCP_SERVER_HOST=localhost                   # MCP 伺服器主機位址
MCP_SERVER_PORT=8080                        # MCP 伺服器連接埠

# 安全性設定
ENABLE_RISK_ASSESSMENT=true                # 啟用風險評估機制
REQUIRE_CONFIRMATION=true                  # 危險操作需要確認
DANGEROUS_COMMANDS_WHITELIST=              # 危險命令白名單（以逗號分隔）

# 監控設定
MONITORING_INTERVAL=30                     # 監控間隔（秒）
CPU_THRESHOLD=80                           # CPU 使用率告警閾值（%）
MEMORY_THRESHOLD=85                        # 記憶體使用率告警閾值（%）
DISK_THRESHOLD=90                          # 磁碟使用率告警閾值（%）

# 日誌設定
LOG_LEVEL=INFO                             # 日誌級別 (DEBUG, INFO, WARNING, ERROR)
LOG_FILE=mcp_agent.log                     # 日誌檔案路徑
```

### 📋 批次命令檔案

建立 `commands.txt` 檔案來執行批次操作：

```bash
# 系統健康檢查腳本
檢查系統狀態
顯示磁碟使用量
檢查記憶體使用情況
列出 CPU 使用率最高的進程
檢查網路連線狀態
顯示系統負載平均值
```

執行批次命令：
```bash
mcp-agent execute --batch commands.txt
```

## 🔒 安全功能詳解

### 🛡️ 多層風險評估系統

#### 風險等級分類
- **🟢 低風險**: 系統資訊查詢、狀態檢查
- **🟡 中風險**: 服務重啟、檔案操作、網路設定
- **🔴 高風險**: 系統服務停止、使用者管理、防火牆設定
- **🚨 極高風險**: 磁碟格式化、系統重開機、檔案刪除

#### 安全檢查規則

1. **檔案操作安全檢查**
   ```python
   # 系統關鍵目錄保護
   critical_paths = ["/etc", "/boot", "/sys", "/proc", "/dev"]

   # 危險操作檢測
   destructive_operations = ["delete", "format", "remove"]
   ```

2. **命令注入防護**
   ```python
   # 危險命令模式檢測
   dangerous_patterns = [
       r"rm\s+(-[rf]+|--recursive|--force)",  # 強制刪除
       r"dd\s+if=/dev/zero",                   # 磁碟清零
       r":(){ :|:& };:",                       # Fork 炸彈
   ]
   ```

3. **服務管理安全檢查**
   ```python
   # 關鍵服務保護
   critical_services = ["ssh", "networking", "firewall"]
   ```

### 🔐 操作確認機制

當執行中高風險操作時，系統會要求確認：

```
⚠️ 風險評估: 高風險操作
📋 操作: 停止 ssh 服務
🎯 影響: 可能導致遠端連線中斷
💡 建議: 確保有本地存取權限或備用連線方式

是否繼續執行？ (y/N):
```

### 📝 操作審計與回滾

所有操作都會記錄完整的審計軌跡：

```json
{
  "operation_id": "op_20241221_143022",
  "timestamp": "2024-12-21T14:30:22Z",
  "user_input": "重啟 nginx 服務",
  "risk_level": "medium",
  "tools_used": ["manage_service"],
  "success": true,
  "execution_time": 3.2,
  "rollback_commands": ["systemctl stop nginx"]
}
```

回滾操作：
```bash
🔧 Operations> rollback 1
🔄 回滾最近 1 個操作...
🔄 正在回滾操作: 重啟 nginx 服務
   ✅ 已執行: systemctl stop nginx
✅ 回滾完成
```

## 📚 程式設計介面 (API)

### 🤖 BaseMCPAgent 基礎類

```python
from mcp_ai_agent.agents import BaseMCPAgent
from mcp_ai_agent.utils.config import Config

# 建立設定物件
config = Config.from_env()

# 初始化代理
agent = BaseMCPAgent(config)
await agent.initialize()

# 處理請求
response = await agent.process_request("檢查系統狀態")
print(response.content)

# 清理資源
await agent.cleanup()
```

### 🔍 MonitoringAgent 監控代理

```python
from mcp_ai_agent.agents import MonitoringAgent

# 建立監控代理
monitor = MonitoringAgent(config)

# 開始監控（會持續運行）
await monitor.run()

# 或者處理特定監控請求
response = await monitor.process_monitoring_request("分析 CPU 使用趨勢")
```

### ⚙️ OperationsAgent 運維代理

```python
from mcp_ai_agent.agents import OperationsAgent

# 建立運維代理
ops_agent = OperationsAgent(config)
await ops_agent.initialize()

# 互動模式
await ops_agent.run()

# 或批次處理
operations = [
    "檢查系統狀態",
    "重啟 nginx 服務",
    "清理暫存檔案"
]
results = await ops_agent.process_batch_operations(operations)
```

### 🔒 自定義安全規則

```python
from mcp_ai_agent.security.risk_assessor import SecurityRule, RiskLevel

# 建立自定義安全規則
custom_rule = SecurityRule(
    name="docker_operations",
    pattern=r"docker\s+(rm|stop|kill)",
    risk_level=RiskLevel.HIGH,
    description="Docker 容器操作"
)

# 新增到風險評估器
risk_assessor.security_rules.append(custom_rule)
```

## 🧪 測試與驗證

### 🔬 單元測試

```bash
# 執行所有測試
python -m pytest tests/ -v

# 測試特定模組
python -m pytest tests/test_agents.py -v

# 生成覆蓋率報告
python -m pytest tests/ --cov=src --cov-report=html
```

### 🏥 系統健康檢查

```bash
# 快速健康檢查
mcp-agent health-check --quick

# 完整系統檢查（包含效能測試）
mcp-agent health-check --format json > health_report.json
```

### 🧪 功能驗證腳本

```bash
# 執行完整功能演示
python setup_example.py

# 驗證 MCP 工具
mcp-agent tools-list

# 測試風險評估
mcp-agent execute "rm -rf /" --dry-run  # 會被安全機制阻止
```

## 📊 效能與最佳化

### ⚡ 效能優化建議

1. **監控間隔調整**
   ```bash
   # 高頻監控（適用於關鍵系統）
   export MONITORING_INTERVAL=10

   # 標準監控
   export MONITORING_INTERVAL=30

   # 低頻監控（適用於穩定系統）
   export MONITORING_INTERVAL=60
   ```

2. **記憶體使用優化**
   ```python
   # 限制歷史資料保存數量
   config.max_history_entries = 1000

   # 定期清理舊資料
   config.cleanup_interval = 3600
   ```

3. **網路連線優化**
   ```bash
   # 使用本地 MCP 伺服器
   export MCP_SERVER_HOST=localhost

   # 調整連線逾時
   export MCP_TIMEOUT=30
   ```

### 📈 監控最佳實務

1. **告警閾值設定**
   ```bash
   # 伺服器等級設定
   CPU_THRESHOLD=70        # 伺服器 CPU
   MEMORY_THRESHOLD=80     # 伺服器記憶體
   DISK_THRESHOLD=85       # 伺服器磁碟

   # 工作站等級設定
   CPU_THRESHOLD=85        # 工作站 CPU
   MEMORY_THRESHOLD=90     # 工作站記憶體
   DISK_THRESHOLD=95       # 工作站磁碟
   ```

2. **自定義監控規則**
   ```python
   # 建立業務相關的監控規則
   custom_rules = [
       AlertRule(
           name="database_connections",
           metric="connection_count",
           threshold=100,
           operator=">=",
           duration=300,
           severity="warning"
       )
   ]
   ```

## 🤝 開發與貢獻

### 🏗️ 專案結構說明

```
mcp_ai_agent/
├── src/                          # 原始碼目錄
│   ├── agents/                   # AI 代理模組
│   │   ├── __init__.py          # 模組初始化
│   │   ├── base_agent.py        # 基礎代理類別
│   │   ├── monitoring_agent.py  # 監控代理實作
│   │   └── operations_agent.py  # 運維代理實作
│   ├── mcp/                     # MCP 協議實作
│   │   ├── __init__.py         # 模組初始化
│   │   └── server.py           # MCP 伺服器實作
│   ├── security/               # 安全性模組
│   │   ├── __init__.py        # 模組初始化
│   │   └── risk_assessor.py   # 風險評估引擎
│   ├── tools/                 # 工具模組
│   │   ├── __init__.py       # 模組初始化
│   │   └── extended_tools.py # 擴展工具集
│   ├── utils/                # 工具程式模組
│   │   ├── __init__.py      # 模組初始化
│   │   └── config.py        # 設定管理
│   └── cli.py               # 命令列介面
├── tests/                   # 測試檔案目錄
├── configs/                 # 設定檔目錄
├── docs/                    # 文件目錄
├── requirements.txt         # Python 依賴套件
├── pyproject.toml          # 專案設定檔
├── setup_example.py        # 安裝與演示腳本
└── README.md               # 專案說明文件
```

### 🔧 開發環境設置

1. **建立開發環境**
   ```bash
   # 建立虛擬環境
   python -m venv mcp_agent_dev
   source mcp_agent_dev/bin/activate

   # 安裝開發依賴
   pip install -e ".[dev]"
   ```

2. **程式碼風格**
   ```bash
   # 程式碼格式化
   black src/ tests/

   # 程式碼檢查
   flake8 src/ tests/

   # 型別檢查
   mypy src/
   ```

### 🔌 擴展開發指南

#### 新增 MCP 工具

```python
# 在 src/mcp/server.py 中新增工具
@server.call_tool()
async def handle_custom_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """處理自定義工具呼叫"""
    if name == "my_custom_tool":
        # 實作您的工具邏輯
        result = await my_custom_logic(arguments)
        return [TextContent(type="text", text=result)]
```

#### 建立自定義代理

```python
from src.agents.base_agent import BaseMCPAgent

class MyCustomAgent(BaseMCPAgent):
    """自定義 AI 代理"""

    async def run(self) -> None:
        """主要執行邏輯"""
        await self.initialize()

        # 實作您的自定義邏輯
        while True:
            user_input = input("輸入指令: ")
            response = await self.process_request(user_input)
            print(response.content)
```

#### 擴展安全規則

```python
from src.security.risk_assessor import SecurityRule, RiskLevel

# 建立新的安全規則
new_rules = [
    SecurityRule(
        name="custom_security_check",
        pattern=r"your_pattern_here",
        risk_level=RiskLevel.HIGH,
        description="自定義安全檢查"
    )
]

# 新增到風險評估器
risk_assessor.security_rules.extend(new_rules)
```

### 📋 貢獻指南

1. **Fork 專案**
   - 前往 GitHub 專案頁面
   - 點擊 "Fork" 按鈕

2. **建立功能分支**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **提交更改**
   ```bash
   git commit -m "feat: 新增驚人功能"
   ```

4. **推送分支**
   ```bash
   git push origin feature/amazing-feature
   ```

5. **建立 Pull Request**
   - 在 GitHub 上建立 Pull Request
   - 詳細描述您的更改

### 🐛 問題回報

如果您發現錯誤或有功能建議，請：

1. 檢查 [現有 Issues](https://github.com/trionnemesis/mcp-ai-agent/issues)
2. 建立新的 Issue，包含：
   - 錯誤描述或功能需求
   - 重現步驟（對於錯誤）
   - 系統環境資訊
   - 相關日誌檔案

## 📄 授權與版權

### 📜 開源授權

本專案採用 MIT 授權協議 - 查看 [LICENSE](LICENSE) 檔案了解詳情。

### 🙏 致謝與第三方套件

- **[Google Gemini SDK](https://ai.google.dev/)** - 提供強大的 AI 語言模型
- **[Model Context Protocol](https://modelcontextprotocol.io/)** - 標準化的模型通信協議
- **[Rich CLI Library](https://github.com/Textualize/rich)** - 美觀的命令列介面
- **[Pydantic](https://pydantic-docs.helpmanual.io/)** - 資料驗證與設定管理
- **[Typer](https://typer.tiangolo.com/)** - 現代化的 CLI 框架
- **[psutil](https://psutil.readthedocs.io/)** - 跨平台系統資訊庫

---

## ⚠️ 重要提醒

1. **🔐 安全性**: 本工具涉及系統管理操作，請務必在測試環境中充分驗證後再用於生產環境
2. **💾 備份**: 執行任何系統操作前，請確保已備份重要資料
3. **🔑 權限**: 某些功能需要 sudo 權限，請謹慎授予
4. **🌐 網路**: 工具需要網路連線以使用 Gemini API
5. **💰 費用**: 使用 Google Gemini API 可能產生費用，請注意您的使用量

