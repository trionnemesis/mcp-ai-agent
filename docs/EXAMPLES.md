# MCP AI Agent 使用範例與最佳實務 📚

## 📋 目錄

1. [快速開始範例](#快速開始範例)
2. [系統監控範例](#系統監控範例)
3. [運維操作範例](#運維操作範例)
4. [批次作業範例](#批次作業範例)
5. [安全操作範例](#安全操作範例)
6. [程式設計介面範例](#程式設計介面範例)
7. [最佳實務指南](#最佳實務指南)
8. [故障排除範例](#故障排除範例)

## 🚀 快速開始範例

### 基本環境設定

```bash
# 1. 複製專案
git clone https://github.com/trionnemesis/mcp-ai-agent.git
cd mcp-ai-agent

# 2. 設定虛擬環境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# 3. 安裝依賴
pip install -r requirements.txt

# 4. 設定環境變數
cp .env.example .env
# 編輯 .env 檔案，設定您的 GEMINI_API_KEY

# 5. 驗證安裝
python setup_example.py
```

### 第一次使用

```bash
# 檢查系統狀態
mcp-agent status

# 執行健康檢查
mcp-agent health-check

# 嘗試簡單命令
mcp-agent execute "檢查系統資訊"

# 啟動互動模式
mcp-agent interactive
```

## 📊 系統監控範例

### 基本監控

```bash
# 開始基本監控（預設 30 秒間隔）
mcp-agent monitor

# 自定義監控間隔（10 秒）
mcp-agent monitor --interval 10

# 設定自定義閾值
mcp-agent monitor \
  --cpu-threshold 85 \
  --memory-threshold 90 \
  --disk-threshold 95

# 監控指定時間（1 小時）
mcp-agent monitor --duration 3600
```

### 進階監控設定

```bash
# 高頻監控（適用於關鍵系統）
export MONITORING_INTERVAL=5
export CPU_THRESHOLD=70
export MEMORY_THRESHOLD=75
mcp-agent monitor --verbose

# 伺服器級監控配置
cat > monitoring_config.env << EOF
MONITORING_INTERVAL=30
CPU_THRESHOLD=70
MEMORY_THRESHOLD=80
DISK_THRESHOLD=85
LOG_LEVEL=INFO
EOF

# 使用配置檔案
source monitoring_config.env
mcp-agent monitor
```

### 監控輸出範例

```
🤖 開始智能系統監控...
📊 監控間隔: 30 秒
⚠️ CPU 閾值: 80%
⚠️ 記憶體閾值: 85%
⚠️ 磁碟閾值: 90%

[2024-12-21 14:30:22] 📊 系統指標:
  CPU: 25% | 記憶體: 68% | 磁碟: 45%

[2024-12-21 14:31:22] ⚠️ 告警 [WARNING]:
  CPU 使用率達到 85% (閾值: 80%)
  🤖 AI 分析: 檢測到 chrome 進程異常高 CPU 使用
  💡 建議: 檢查瀏覽器擴展或重啟瀏覽器

[2024-12-21 14:32:22] ✅ 系統恢復正常
  CPU: 45% | 記憶體: 70% | 磁碟: 45%
```

## ⚙️ 運維操作範例

### 系統資訊查詢

```bash
# 基本系統資訊
mcp-agent execute "顯示系統基本資訊"

# 詳細系統資訊
mcp-agent execute "顯示詳細系統資訊包含 CPU 核心數和負載平均"

# 記憶體資訊
mcp-agent execute "檢查記憶體使用情況"

# 磁碟使用情況
mcp-agent execute "顯示所有磁碟分割區的使用情況"
```

### 服務管理

```bash
# 服務狀態檢查
mcp-agent execute "檢查 nginx 服務狀態"
mcp-agent execute "顯示所有正在運行的 systemd 服務"

# 服務控制
mcp-agent execute "重啟 apache2 服務"
mcp-agent execute "停止 mysql 服務"
mcp-agent execute "啟動 docker 服務"

# 服務配置
mcp-agent execute "啟用 nginx 服務開機自啟"
mcp-agent execute "停用 apache2 服務開機自啟"
```

### 進程管理

```bash
# 進程查看
mcp-agent execute "顯示 CPU 使用率最高的 10 個進程"
mcp-agent execute "顯示記憶體使用量最大的進程"
mcp-agent execute "列出所有 python 相關的進程"

# 進程分析
mcp-agent execute "分析系統中的資源消耗異常進程"
mcp-agent execute "查找佔用 80 埠的進程"
```

### 網路診斷

```bash
# 連線測試
mcp-agent execute "ping google.com 測試網路連線"
mcp-agent execute "測試到 8.8.8.8 的連線延遲"

# 網路狀態
mcp-agent execute "顯示所有網路介面資訊"
mcp-agent execute "檢查目前開放的網路埠"
mcp-agent execute "顯示網路連線統計"

# 路由診斷
mcp-agent execute "追蹤到 github.com 的網路路由"
```

### 日誌分析

```bash
# 系統日誌
mcp-agent execute "顯示最近 50 行系統日誌"
mcp-agent execute "顯示過去 1 小時的錯誤日誌"

# 服務日誌
mcp-agent execute "檢查 nginx 服務的最新日誌"
mcp-agent execute "分析 apache 日誌中的錯誤模式"

# 日誌搜尋
mcp-agent execute "在系統日誌中搜尋 'failed' 關鍵字"
mcp-agent execute "尋找包含 'authentication failure' 的日誌條目"
```

## 📋 批次作業範例

### 系統健康檢查腳本

建立 `health_check.txt`:
```
檢查系統基本資訊
顯示 CPU 和記憶體使用情況
檢查磁碟空間使用量
列出 CPU 使用率最高的 5 個進程
檢查系統負載平均值
顯示網路介面狀態
檢查重要服務狀態：nginx, mysql, ssh
顯示最近 10 行系統錯誤日誌
```

執行批次檢查：
```bash
mcp-agent execute --batch health_check.txt
```

### 日常維護腳本

建立 `daily_maintenance.txt`:
```
檢查系統更新
清理系統暫存檔案
檢查磁碟使用量
備份重要配置檔案
檢查系統日誌中的異常
重啟過期的服務
檢查網路連線狀態
產生系統狀態報告
```

執行維護腳本：
```bash
mcp-agent execute --batch daily_maintenance.txt > daily_report.log
```

### 安全檢查腳本

建立 `security_audit.txt`:
```
執行基本系統安全審計
檢查不安全的檔案權限
掃描開放的網路埠
檢查失敗的登入嘗試
分析系統使用者帳戶
檢查 SSH 配置安全性
審計 sudo 使用記錄
檢查系統完整性
```

執行安全檢查：
```bash
mcp-agent execute --batch security_audit.txt --format json > security_report.json
```

## 🔒 安全操作範例

### 風險評估演示

```bash
# 低風險操作（自動執行）
mcp-agent execute "檢查系統狀態"

# 中風險操作（需要確認）
mcp-agent execute "重啟 nginx 服務"
# 輸出：⚠️ 這是一個中風險操作，是否繼續？ (y/N):

# 高風險操作（需要確認和說明）
mcp-agent execute "停止 ssh 服務"
# 輸出：
# ⚠️ 風險評估: 高風險操作
# 📋 操作: 停止 ssh 服務
# 🎯 影響: 可能導致遠端連線中斷
# 💡 建議: 確保有本地存取權限
# 是否繼續執行？ (y/N):

# 極高風險操作（會被阻止）
mcp-agent execute "rm -rf /" --dry-run
# 輸出：❌ 此操作被安全機制阻止
```

### 安全配置範例

```bash
# 啟用嚴格安全模式
export ENABLE_RISK_ASSESSMENT=true
export REQUIRE_CONFIRMATION=true

# 設定危險命令白名單
export DANGEROUS_COMMANDS_WHITELIST="systemctl restart nginx,systemctl reload apache2"

# 執行操作
mcp-agent execute "重啟 nginx 服務"  # 會被白名單允許
```

### 操作審計範例

```bash
# 檢視操作歷史
mcp-agent interactive
# 進入互動模式後：
🔧 Operations> history

# 輸出範例：
📜 操作歷史 (最近 10 項):
 1. ✅ 檢查系統狀態
    時間: 2.3s | 工具: get_system_info | 風險: low
 2. ✅ 重啟 nginx 服務
    時間: 5.1s | 工具: manage_service | 風險: medium
 3. ❌ 停止 ssh 服務
    錯誤: 用戶取消操作 | 風險: high

# 回滾操作
🔧 Operations> rollback 1
🔄 回滾最近 1 個操作...
✅ 已執行回滾命令: systemctl stop nginx
```

## 💻 程式設計介面範例

### 基本 API 使用

```python
import asyncio
from mcp_ai_agent.agents import OperationsAgent
from mcp_ai_agent.utils.config import Config

async def main():
    # 載入配置
    config = Config.from_env()

    # 建立代理
    agent = OperationsAgent(config)
    await agent.initialize()

    try:
        # 執行操作
        response = await agent.process_request("檢查系統狀態")
        print(f"結果: {response.content}")
        print(f"信心度: {response.confidence}")
        print(f"風險等級: {response.risk_level}")

    finally:
        await agent.cleanup()

# 執行
asyncio.run(main())
```

### 監控代理範例

```python
import asyncio
from mcp_ai_agent.agents import MonitoringAgent
from mcp_ai_agent.utils.config import Config

async def monitoring_example():
    config = Config.from_env()

    # 自定義監控配置
    config.monitoring_interval = 10
    config.cpu_threshold = 75.0
    config.memory_threshold = 80.0

    monitor = MonitoringAgent(config)

    # 取得監控狀態
    status = await monitor.get_monitoring_status()
    print(f"監控狀態: {status}")

    # 處理特定監控請求
    response = await monitor.process_monitoring_request(
        "分析過去 30 分鐘的 CPU 使用趨勢"
    )
    print(f"分析結果: {response.content}")

asyncio.run(monitoring_example())
```

### 批次處理範例

```python
import asyncio
from mcp_ai_agent.agents import OperationsAgent
from mcp_ai_agent.utils.config import Config

async def batch_operations_example():
    config = Config.from_env()
    agent = OperationsAgent(config)
    await agent.initialize()

    # 定義批次操作
    operations = [
        "檢查系統狀態",
        "顯示磁碟使用量",
        "列出正在運行的服務",
        "檢查網路連線"
    ]

    try:
        # 執行批次操作
        results = await agent.process_batch_operations(operations)

        # 處理結果
        for i, result in enumerate(results):
            print(f"操作 {i+1}: {operations[i]}")
            print(f"狀態: {'成功' if result.success else '失敗'}")
            print(f"執行時間: {result.execution_time:.2f}s")
            print(f"使用工具: {', '.join(result.tools_used)}")
            print("-" * 40)

    finally:
        await agent.cleanup()

asyncio.run(batch_operations_example())
```

### 自定義安全規則範例

```python
from mcp_ai_agent.security.risk_assessor import SecurityRule, RiskLevel, RiskAssessor
from mcp_ai_agent.utils.config import Config

# 建立自定義安全規則
custom_rules = [
    SecurityRule(
        name="docker_container_operations",
        pattern=r"docker\s+(stop|kill|rm)\s+",
        risk_level=RiskLevel.HIGH,
        description="Docker 容器刪除或停止操作"
    ),
    SecurityRule(
        name="database_operations",
        pattern=r"(mysql|postgresql|mongodb).*drop\s+",
        risk_level=RiskLevel.CRITICAL,
        description="資料庫刪除操作"
    ),
    SecurityRule(
        name="firewall_changes",
        pattern=r"(iptables|ufw|firewall-cmd)\s+",
        risk_level=RiskLevel.HIGH,
        description="防火牆配置變更"
    )
]

# 使用自定義規則
config = Config.from_env()
risk_assessor = RiskAssessor(config)
risk_assessor.security_rules.extend(custom_rules)

# 測試風險評估
async def test_risk_assessment():
    commands = [
        "docker stop web-server",  # 高風險
        "mysql drop database test",  # 極高風險
        "ls -la",  # 低風險
    ]

    for cmd in commands:
        risk_level = await risk_assessor.assess_tool_call(
            "execute_command",
            {"command": cmd}
        )
        print(f"命令: {cmd}")
        print(f"風險等級: {risk_level}")
        print("-" * 30)

import asyncio
asyncio.run(test_risk_assessment())
```

## 📖 最佳實務指南

### 🔧 系統配置最佳實務

#### 生產環境配置

```bash
# .env.production
GEMINI_API_KEY=your_production_api_key
GEMINI_MODEL=gemini-1.5-pro

# 安全設定
ENABLE_RISK_ASSESSMENT=true
REQUIRE_CONFIRMATION=true
DANGEROUS_COMMANDS_WHITELIST="systemctl reload nginx,systemctl restart php8.1-fpm"

# 監控設定（生產環境較保守）
MONITORING_INTERVAL=60
CPU_THRESHOLD=70
MEMORY_THRESHOLD=80
DISK_THRESHOLD=85

# 日誌設定
LOG_LEVEL=WARNING
LOG_FILE=/var/log/mcp_agent.log
```

#### 開發環境配置

```bash
# .env.development
GEMINI_API_KEY=your_development_api_key
GEMINI_MODEL=gemini-1.5-pro

# 安全設定（開發環境較寬鬆）
ENABLE_RISK_ASSESSMENT=true
REQUIRE_CONFIRMATION=false

# 監控設定（開發環境較頻繁）
MONITORING_INTERVAL=10
CPU_THRESHOLD=85
MEMORY_THRESHOLD=90
DISK_THRESHOLD=95

# 日誌設定
LOG_LEVEL=DEBUG
LOG_FILE=./dev_mcp_agent.log
```

### 🚨 監控最佳實務

#### 告警配置策略

```python
# 分層告警策略
ALERT_RULES = {
    "critical_services": {
        "services": ["ssh", "networking", "systemd"],
        "action": "immediate_alert",
        "escalation": "phone_call"
    },
    "web_services": {
        "services": ["nginx", "apache2", "php-fpm"],
        "action": "alert_after_2min",
        "escalation": "email"
    },
    "database_services": {
        "services": ["mysql", "postgresql", "redis"],
        "action": "alert_after_1min",
        "escalation": "slack"
    }
}

# 資源使用告警
RESOURCE_THRESHOLDS = {
    "cpu": {"warning": 70, "critical": 90},
    "memory": {"warning": 80, "critical": 95},
    "disk": {"warning": 85, "critical": 98},
    "load": {"warning": 2.0, "critical": 5.0}
}
```

#### 監控腳本範例

```bash
#!/bin/bash
# production_monitoring.sh

# 設定環境
source /etc/mcp-agent/production.env

# 啟動監控（背景執行）
nohup mcp-agent monitor \
  --cpu-threshold $CPU_THRESHOLD \
  --memory-threshold $MEMORY_THRESHOLD \
  --disk-threshold $DISK_THRESHOLD \
  > /var/log/mcp_monitoring.log 2>&1 &

echo "監控已啟動，PID: $!"
echo "日誌位置: /var/log/mcp_monitoring.log"
```

### 🔐 安全最佳實務

#### 權限管理

```bash
# 建立專用使用者
sudo useradd -r -s /bin/false mcp-agent

# 設定最小權限
sudo usermod -a -G systemd-journal mcp-agent  # 讀取日誌
sudo usermod -a -G adm mcp-agent              # 系統管理

# sudoers 配置
echo "mcp-agent ALL=(ALL) NOPASSWD: /bin/systemctl status *, /bin/systemctl restart nginx, /bin/systemctl reload apache2" | sudo tee /etc/sudoers.d/mcp-agent
```

#### 網路安全

```bash
# 防火牆配置
sudo ufw allow from 127.0.0.1 to any port 8080  # MCP 伺服器
sudo ufw deny 8080                               # 拒絕外部存取

# API 金鑰安全
chmod 600 /etc/mcp-agent/.env
chown mcp-agent:mcp-agent /etc/mcp-agent/.env
```

### 📊 效能最佳實務

#### 資源使用優化

```python
# 配置優化
PERFORMANCE_CONFIG = {
    # 限制歷史資料量
    "max_history_entries": 1000,

    # 監控間隔調整
    "monitoring_intervals": {
        "critical_systems": 10,    # 關鍵系統高頻監控
        "normal_systems": 30,      # 一般系統標準監控
        "stable_systems": 60       # 穩定系統低頻監控
    },

    # 併發限制
    "max_concurrent_operations": 5,

    # 快取設定
    "tool_cache_ttl": 300,        # 工具快取 5 分鐘
    "metrics_cache_ttl": 60       # 指標快取 1 分鐘
}
```

## 🚨 故障排除範例

### 常見問題診斷

#### API 連線問題

```bash
# 檢查 API 金鑰
echo $GEMINI_API_KEY

# 測試 API 連線
python -c "
import google.generativeai as genai
import os
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
try:
    model = genai.GenerativeModel('gemini-1.5-pro')
    response = model.generate_content('Hello')
    print('API 連線正常')
except Exception as e:
    print(f'API 連線失敗: {e}')
"
```

#### MCP 服務問題

```bash
# 檢查 MCP 伺服器狀態
mcp-agent tools-list

# 如果工具列表為空，檢查伺服器啟動
python -m mcp_ai_agent.mcp.server

# 檢查埠佔用
netstat -tlnp | grep 8080
```

#### 權限問題

```bash
# 檢查目前使用者權限
whoami
groups

# 檢查 sudo 權限
sudo -l

# 測試系統命令執行
mcp-agent execute "檢查我的權限" --dry-run
```

### 日誌分析

```bash
# 檢查應用程式日誌
tail -f /var/log/mcp_agent.log

# 篩選錯誤日誌
grep "ERROR" /var/log/mcp_agent.log | tail -10

# 檢查系統日誌
journalctl -u mcp-agent -f

# 分析效能問題
mcp-agent execute "分析系統效能瓶頸"
```

### 偵錯模式

```bash
# 啟用詳細日誌
export LOG_LEVEL=DEBUG
mcp-agent execute "測試命令" --verbose

# 模擬模式測試
mcp-agent execute "重啟服務" --dry-run

# 跳過確認進行測試
mcp-agent execute "檢查高風險操作" --no-confirm --dry-run
```

### 效能調優

```bash
# 監控系統資源使用
mcp-agent execute "分析 MCP Agent 本身的資源使用"

# 效能測試
time mcp-agent execute "執行複雜系統分析"

# 併發測試
for i in {1..5}; do
  mcp-agent execute "檢查系統狀態" &
done
wait
```

---

## 📚 總結

這些範例涵蓋了 MCP AI Agent 的主要使用場景，從基本操作到進階配置，從單一命令到批次處理，從開發環境到生產部署。

**關鍵要點**:

1. **從簡單開始**: 先熟悉基本命令，再逐步使用進階功能
2. **安全第一**: 始終注意操作的風險等級和安全影響
3. **監控為本**: 建立完整的監控和告警機制
4. **文檔記錄**: 記錄所有重要操作和配置變更
5. **持續改進**: 根據使用經驗調整配置和工作流程

透過這些範例和最佳實務，您可以充分發揮 MCP AI Agent 的潛力，建立安全、高效的智能運維系統。