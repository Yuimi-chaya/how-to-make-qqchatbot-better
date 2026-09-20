# How to Make QQ Chatbot Better

**让 QQ 上的角色更好聊：从宿主能力、模型表现、人设质量，到 AstrBot 的具体实践。**

你可能已经把机器人接上了 QQ，也给它写了一份喜欢的人设。它能回答问题，却不一定好聊：你补充一句，它还在把上一轮的几条消息慢慢发完；你随手发张表情包，它认真解释画面；提示词越改越长，角色反倒越来越拘谨。

这本书从这些实际体验出发。不追求把机器人装成一个无法识破的真人，而是让它更能接住当前的互动，保留人物特点，也把答应做的事情真正做好。

核心思路很简单：

- **宿主能力**决定模型看见什么、什么时候被调用、消息怎样送出、能做哪些事。不要把接收、分段、打断和工具执行问题全交给提示词。
- **模型表现**决定它如何理解上下文、选择表达、使用图片与工具。通用能力强或某条回复惊艳，不等于长期私聊合适。
- **人设质量**决定对面是谁、在意什么、你们是什么关系、怎样表达。不要用一长串禁令，把所有角色修成同一种“自然”。

三者会互相影响，不是各占三分之一。一个能只发表情的宿主，不保证模型选图贴切；一份写得很好的角色卡，也没法取消宿主已经排队的旧回复。

## 从哪里开始

**还没有搭好机器人**：先读第 1、2 章，再到第 7 章完成 AstrBot + NapCat 的最小安装；收到第一条回复以后，再改善体验。

**已经能聊天，但感觉不对**：从第 3 章开始。先把消息节奏和表情包能力弄清楚，再决定换模型还是改人设。

**主要想写角色提示词**：读第 5 章。传统第一人称与写作者视角都可以用；本书不要求先选择某一派。

| 章节 | 读完能解决什么 |
| --- | --- |
| [1. 我们想要怎样的 LLM RP](chapters/01-what-we-want.md) | 区分“回答得好”和“相处起来对味”，确定自己的目标 |
| [2. QQ 聊天背后的整条链路](chapters/02-the-stack.md) | 分清 AstrBot、模型、OneBot、LLBot、NapCat 各自做什么 |
| [3. 宿主先学会等人说完](chapters/03-host-and-turns.md) | 理解分段与轮次的不对称，用 TurnFlow 一类能力处理补充与打断 |
| [4. 表情包也是完整的回应](chapters/04-memes-and-images.md) | 让机器人能不说正文，只发一个合适的表情；理解分类与语义检索 |
| [5. 人设不只是口吻](chapters/05-persona.md) | 根据自己的偏好写、判断和修改提示词，保留人物而不堆规则 |
| [6. 选一个适合相处的模型](chapters/06-models.md) | 在实际宿主里比较语感、上下文、工具、延迟与成本 |
| [7. 实例：AstrBot + NapCat + 宝塔](chapters/07-astrbot-deployment.md) | 搭好基础链路，理解网络、凭据、模型与消息测试 |
| [8. 记忆、时间与主动联系](chapters/08-memory-and-tools.md) | 把“记得”和“做到”落实到真实能力，同时保留自然的主动性 |
| [9. 感觉不对时，怎么找原因](chapters/09-debugging.md) | 用少量有区分力的检查定位问题，避免无限返工 |
| [10. 插件怎么加，系统怎么养](chapters/10-maintenance.md) | 逐项扩展、检查联动、备份升级，让日常使用稳定下来 |

正文中的聊天例子均为教学虚构，不是模型实测成绩，也不是必须照抄的角色台词。

## 用到的项目

- [AstrBot](https://github.com/AstrBotDevs/AstrBot)：本书的宿主实例。
- [LuckyLilliaBot / LLBot](https://github.com/LLOneBot/LuckyLilliaBot) 与 [LLOneBot 旧入口](https://github.com/LLOneBot/LLOneBot)：QQ 协议端选项。
- [NapCatQQ](https://github.com/NapNeko/NapCatQQ) 与 [NapCat-Docker](https://github.com/NapNeko/NapCat-Docker)：本书安装实例使用的协议端与容器项目。
- [OneBot v11](https://github.com/botuniverse/onebot-11)、[aiocqhttp](https://github.com/nonebot/aiocqhttp)：接口标准与相关 Python SDK，不是同一个概念。
- [TurnFlow](https://github.com/Yuimi-chaya/astrbot_plugin_turnflow)：私聊消息防抖与未完成回复的动态撤回。
- [表情包管理器](https://github.com/anka-afk/astrbot_plugin_meme_manager)：表情分类、语义检索与发送。
- [Role Prompt Authoring](https://github.com/Yuimi-chaya/llm-rp-role-prompt-authoring)：提示词编写、审查与修改方法的参考来源，不是必装运行插件。

项目功能与文档核对于 **2026-09-20**，具体参照提交见[来源索引](sources/README.md)。版本会变化，链接到项目不表示所有版本、平台和插件组合都经过本书实机验证。

## 延伸阅读

仓库收录了五篇[文章副本](articles/README.md)，包括人设写作、写作者视角、插件开发、部署教程及 AI 陪伴随笔。正文图片已放在 `assets/`，使用相对路径；直接在 GitHub 打开文章 `.md` 即可加载，不需要部署博客或启用 Git LFS。

这些文章保留了作者不同阶段的思考，不强行改写成一致结论。特别是气泡计数、正反例选择、提示词效果归因和旧部署配置，请先看文章目录中的阅读说明。

## 关于这本书

作者：**Yuimi-chaya**。正文在作者实践与公开文章基础上，使用 AI 辅助整理、核对和编写。TurnFlow 与 Role Prompt Authoring 也是作者维护的项目；推荐它们时会说明适用问题和边界，不把作者身份当成效果证据。

本书主要讨论一对一 QQ 私聊，不是群聊运营、批量发信或绕过平台限制的教程。第三方 QQ 协议端的可用性、账号风险和平台规则需要自行核对；“接上了”不代表获得平台授权或永远稳定。

原创文字和改编文字采用 CC BY-NC-SA 4.0；文章原有代码许可、图片及第三方内容单独处理，见[许可与署名](LICENSE.md)。配图不因为随书提供就自动获得同样的再利用许可。
