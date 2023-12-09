# Kasumi

## Kasumi Bot  

BanGGame Collection

预定计划（非实际）：
- 猜卡面：kumo    
- 猜歌（音频）：WindowsSov8    
- 猜曲（封面）：WindowsSov8    
- 猜谱面：Gitai@zhaomaoniu     
- 邦邦jjc：nil    
- 邦邦pvp：arsbot@xianganhuasheng     
- 马卡龙塔：kumo

技术支持：
- Satori & Koishi    
- 张仪宇@il-harper    

形象设计：
- 头像：Ray@b站：亖｜Ray｜亖    

机器人主体：Gitai@zhaomaoniu   
项目地址：github.com/…   
服务器运维：kumo

*…More with you.*

***

## dev

**dependencies:**
`python3.10+`
```bash
pip install flask websocket-client PyYAML requests schedule pillow
```

Bridge实现：

- 群聊: 
  - [x] 文字消息（自动被动）
  - [x] 富媒体消息（自动被动）（暂不支持音频）
  - [x] 5分钟内爽发（seq自动++）

- 频道: 
  - [x] 文字消息
  - [x] 富媒体消息
  - [x] 5分钟内爽发


- [x] h()函数: 主动选择依赖被动消息的msg_id


- [x] session.command: 用于处理命令


