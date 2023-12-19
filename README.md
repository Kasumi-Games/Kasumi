# Kasumi

## Kasumi Bot  

BanGame Collection Bot

已实现：
- 猜卡面：kumo 
- 猜谱面：Gitai@zhaomaoniu  
- 
预定计划（非实际）：
- 猜歌（音频）：WindowsSov8    
- 猜曲（封面）：WindowsSov8    
- 猜谱面：Gitai@zhaomaoniu     
- 邦邦jjc：nil    
- 邦邦pvp：arsbot@xianganhuasheng     
- 马卡龙塔：kumo
- <暂未揭晓> KanonBot@SuperGuGu

技术支持：
- Satori & Koishi    
- 张仪宇@il-harper

机器人框架：[TomorinBOT](https://github.com/kumoSleeping/TomorinBot)   
机器人主体：Gitai@zhaomaoniu   
服务器运维：kumo   
形象设计（暂定）：(⬇两只咕咕)
- 头像：Ray@b站：亖丨Ray丨亖    
- 头像2：忽-悠人@b站：千早愛音_公式   

*…More with you.*

***

## dev

**dependencies:**
`python3.10+`
```bash
pip install flask websocket-client PyYAML requests schedule Pillow bestdori-api fuzzywuzzy
```

Bridge实现针对QQ特性：

- 群聊: 
  - [x] 文字消息（自动被动）
  - [x] 富媒体消息（自动被动）（暂不支持音频）
  - [x] 5分钟内爽发（seq自动++）

- 频道: 
  - [x] 文字消息
  - [x] 富媒体消息
  - [x] 5分钟内爽发


- [x] h()函数: 主动选择依赖被动消息的msg_id


