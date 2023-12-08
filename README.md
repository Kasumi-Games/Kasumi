# Kasumi
Kasumi Bot

**dependencies:**
`python3.10+`
```bash
pip install flask websocket-client PyYAML requests schedule
```

Bridge实现：

- 群聊: 
  - [x] 文字消（自动被动）
  - [x] 富媒体消息（自动被动）
  - [x] 5分钟内爽发（seq自动++）

- 频道: 
  - [x] 文字消息（自动被动）
  - [x] 富媒体消息（自动被动）
  - [ ] 5分钟内爽发


- [x] h()函数: 主动选择依赖被动消息的msg_id


- [x] session.command: 用于处理命令


