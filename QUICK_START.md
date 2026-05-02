# 🚀 5分钟快速启动指南

## 📋 前置检查清单

在开始之前，确保你有：

- [ ] Mac/Linux电脑或VPS（Windows需要WSL）
- [ ] 能访问Google/OpenAI的代理（翻墙工具）
- [ ] Telegram账号
- [ ] 信用卡（用于购买API服务）

---

## 🎯 Step 1: 安装Hermes Agent

### Mac/Linux
```bash
# 使用pip安装
pip install hermes-agent

# 验证安装
hermes --version
```

### Windows (WSL)
```bash
# 先安装WSL2
wsl --install

# 然后在WSL中安装
pip install hermes-agent
```

---

## 🔑 Step 2: 配置API密钥

### 2.1 获取DeepSeek API Key
1. 访问 https://platform.deepseek.com
2. 注册账号并充值（建议$20起）
3. 创建API Key并复制

### 2.2 创建Telegram Bot
1. 在Telegram中搜索 @BotFather
2. 发送 `/newbot` 创建机器人
3. 按提示设置名称，获取Bot Token
4. 复制Token（格式：`1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`）

### 2.3 配置Hermes
```bash
# 编辑配置文件
nano ~/.hermes/config.yaml
```

填入以下内容：
```yaml
llm:
  provider: deepseek
  api_key: "你的DeepSeek API Key"

telegram:
  bot_token: "你的Telegram Bot Token"
  
proxy:
  http_proxy: "http://127.0.0.1:7890"  # 改成你的代理地址
  https_proxy: "http://127.0.0.1:7890"
```

保存并退出（Ctrl+X → Y → Enter）

---

## 📦 Step 3: 部署脚本

### 3.1 复制脚本文件
```bash
# 创建脚本目录
mkdir -p ~/.hermes/scripts

# 复制所有脚本
cp scripts/*.py ~/.hermes/scripts/
```

### 3.2 启动Hermes Gateway
```bash
# 启动Gateway（后台运行）
hermes gateway start

# 验证状态
hermes gateway status
```

### 3.3 创建定时任务

在Telegram中找到你的Bot，发送以下消息：

```
创建定时任务：
1. 每2小时运行内容套利脚本
2. 每小时运行Meme监控
3. 每天早上9点运行加密市场日报
```

或者使用命令行：
```bash
# 内容套利（每2小时）
hermes cronjob create \
  --schedule "every 2h" \
  --script "~/.hermes/scripts/content_arbitrage.py" \
  --name "内容套利"

# Meme监控（每小时）
hermes cronjob create \
  --schedule "every 1h" \
  --script "~/.hermes/scripts/meme_monitor.py" \
  --name "Meme监控"

# 加密日报（每天9:00）
hermes cronjob create \
  --schedule "0 9 * * *" \
  --script "~/.hermes/scripts/crypto_market_monitor.py" \
  --name "加密日报"
```

---

## ✅ Step 4: 验证运行

### 4.1 检查定时任务
```bash
hermes cronjob list
```

你应该看到类似输出：
```
ID: abc123  | 内容套利  | every 2h | ✓ enabled
ID: def456  | Meme监控  | every 1h | ✓ enabled
ID: ghi789  | 加密日报  | 0 9 * * * | ✓ enabled
```

### 4.2 手动测试
```bash
# 手动运行一次内容套利
hermes cronjob run abc123

# 查看日志
hermes cronjob logs abc123
```

### 4.3 检查Telegram推送
- 打开你的Telegram Bot对话
- 应该能看到推送的内容
- 如果没有，检查Bot Token是否正确

---

## 🎉 完成！

现在你的AI赚钱系统已经开始运行了！

### 接下来做什么？

1. **监控运行** - 前几天密切关注Telegram推送，确保一切正常
2. **优化配置** - 根据实际效果调整定时任务频率
3. **添加返佣链接** - 在推广脚本中填入你的返佣链接
4. **扩展渠道** - 逐步开通更多平台账号（小红书、即刻、B站等）

---

## 🆘 遇到问题？

### 常见问题

**Q: 脚本运行报错怎么办？**
A: 查看详细日志 `hermes cronjob logs <job_id>`，通常是API配置或代理问题

**Q: Telegram收不到推送？**
A: 检查Bot Token是否正确，Gateway是否正常运行

**Q: 代理连接失败？**
A: 确认代理地址和端口正确，代理软件正在运行

**Q: API费用太高？**
A: 可以降低定时任务频率，或使用更便宜的模型

### 获取帮助

- 📧 邮箱: support@dao-jie.shop
- 💬 Telegram: @daojie_support
- 📚 完整文档: 查看 `DEPLOYMENT_GUIDE.md`

---

**祝你赚钱顺利！💰**
