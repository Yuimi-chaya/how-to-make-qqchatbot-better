# 来源索引

[返回目录](../README.md) · [文章副本](../articles/README.md)

核对日期：**2026-09-20**。下表中的提交是本书编写时读取的快照，不表示最新稳定发行版，也不表示已在真实 QQ 环境测试。移动中的项目首页便于继续阅读，固定提交用于追溯本书的判断依据。

第 7、8 章关于网页端口、Docker 映射和上下文压缩的说明于 **2026-09-24** 另行对照当前 [AstrBot 宝塔文档](https://docs.astrbot.app/deploy/astrbot/btpanel.html)、[上下文压缩文档](https://docs.astrbot.app/use/context-compress.html)、[NapCat-Docker README](https://github.com/NapNeko/NapCat-Docker) 和 [Docker 端口发布与防火墙文档](https://docs.docker.com/engine/network/port-publishing/) 复核；原项目快照提交没有随之更新。部署建议仍未在真实服务器上联调。

第 4、8 章新增的视觉转述与会话迁移说明于 **2026-09-24** 对照 [AstrBot 图片转述配置](https://docs.astrbot.app/dev/astrbot-config.html)、[内置新建对话指令](https://docs.astrbot.app/use/command.html)和 [WebUI 对话管理](https://docs.astrbot.app/use/webui.html) 复核。示例中的 `content` 数组是通用消息结构示意，不声称 WebUI 可直接导入，也不声称目标模型已经验收。

## 文章来源

上游：[Yuimi-chaya/Yuimi-chaya.github.io](https://github.com/Yuimi-chaya/Yuimi-chaya.github.io)。

统一参照提交：`4fd072b8efb10e34403037d6fda2f068d1acd934`。

| 本地副本 | 原文 |
| --- | --- |
| [写作视角](../articles/llm-rp-role-prompt-authoring-research.zh-CN.md) | [固定原文](https://github.com/Yuimi-chaya/Yuimi-chaya.github.io/blob/4fd072b8efb10e34403037d6fda2f068d1acd934/src/content/blog/llm-rp-role-prompt-authoring-research.zh-CN.md) |
| [第一人称人设](../articles/astrbot-roleplay-persona-notes.md) | [固定原文](https://github.com/Yuimi-chaya/Yuimi-chaya.github.io/blob/4fd072b8efb10e34403037d6fda2f068d1acd934/src/content/blog/astrbot-roleplay-persona-notes.md) |
| [插件开发经验](../articles/astrbot-plugin-dev-experience.md) | [固定原文](https://github.com/Yuimi-chaya/Yuimi-chaya.github.io/blob/4fd072b8efb10e34403037d6fda2f068d1acd934/src/content/blog/astrbot-plugin-dev-experience.md) |
| [宝塔部署](../articles/astrbot-napcat-baota-deploy.md) | [固定原文](https://github.com/Yuimi-chaya/Yuimi-chaya.github.io/blob/4fd072b8efb10e34403037d6fda2f068d1acd934/src/content/blog/astrbot-napcat-baota-deploy.md) |
| [AI 陪伴随笔](../articles/is-it-strange-to-feel-for-ai.md) | [固定原文](https://github.com/Yuimi-chaya/Yuimi-chaya.github.io/blob/4fd072b8efb10e34403037d6fda2f068d1acd934/src/content/blog/is-it-strange-to-feel-for-ai.md) |

每篇正文的编辑说明列在副本开头。完整文章和配图的路径、获取地址、哈希及图片尺寸见 [import-manifest.json](import-manifest.json)。清单记录的是该快照，不自动跟随博客更新。

## 项目与技术依据

| 项目 | 参照提交与入口 | 用于本书哪部分 |
| --- | --- | --- |
| AstrBot | [`6914bc3`](https://github.com/AstrBotDevs/AstrBot/tree/6914bc3aa61e14ca9a9c2cb37a0f9ec1ff5d6334) | 宿主、接入、主动任务与上下文能力 |
| LLBot / LuckyLilliaBot | [`9f374f6` README](https://github.com/LLOneBot/LuckyLilliaBot/blob/9f374f6442b6c38a95841fc1d472cf6d8ea6149e/README.md) | 项目名称、协议端选项；不据此声称完整部署已验证 |
| NapCatQQ | [`2049e64`](https://github.com/NapNeko/NapCatQQ/tree/2049e64260d378e9f1f1f318ae033347d46ab994) | QQ 协议端原项目 |
| NapCat-Docker | [`f0599fb` README](https://github.com/NapNeko/NapCat-Docker/blob/f0599fb2eef4e9007aed72501849e2ca3eeaccdf/README.md) | 镜像、容器目录、WebUI |
| NapCat-Docker AstrBot 模板 | [同提交 compose/astrbot.yml](https://github.com/NapNeko/NapCat-Docker/blob/f0599fb2eef4e9007aed72501849e2ca3eeaccdf/compose/astrbot.yml) | 同网络、媒体共享路径；本书另行收紧端口并选择手动连接 |
| OneBot v11 | [`d4456ee`](https://github.com/botuniverse/onebot-11/tree/d4456ee706f9ada9c2dfde56a2bcfc69752600e4) | 标准与实现端的区别 |
| aiocqhttp | [`2520928`](https://github.com/nonebot/aiocqhttp/tree/2520928d2373f5be71059600b832e230a39ccdb9) | Python SDK 原项目 |
| TurnFlow | [`87a79b6` README](https://github.com/Yuimi-chaya/astrbot_plugin_turnflow/blob/87a79b69948d407605d58a7a375125790b736a6d/README.md) | 防抖、中断、撤回与兼容边界 |
| 表情包管理器 | [`92de79e` README](https://github.com/anka-afk/astrbot_plugin_meme_manager/blob/92de79e441bb55d7159067edcc48adbb2d2f4015/README.md) | 分类、纯图、语义化、使用规则及资源准备 |
| 表情包管理器开发文档 | [同提交 DEVELOPMENT.md](https://github.com/anka-afk/astrbot_plugin_meme_manager/blob/92de79e441bb55d7159067edcc48adbb2d2f4015/DEVELOPMENT.md) | 流式标签处理、图片发送时机、第三方联动 |
| Role Prompt Authoring | [`fb3c0e9`](https://github.com/Yuimi-chaya/llm-rp-role-prompt-authoring/tree/fb3c0e96020475122b47696e91d2093bfff851d4) | 偏好保全、最小修改、停止无效迭代与宿主泛化 |

## AstrBot 文档入口

公开站点会更新。上述 AstrBot 提交中的 `docs/zh/` 是本次主要技术参照：

- [OneBot v11](https://github.com/AstrBotDevs/AstrBot/blob/6914bc3aa61e14ca9a9c2cb37a0f9ec1ff5d6334/docs/zh/platform/aiocqhttp.md) / [阅读页](https://docs.astrbot.app/platform/aiocqhttp.html)
- [宝塔部署](https://github.com/AstrBotDevs/AstrBot/blob/6914bc3aa61e14ca9a9c2cb37a0f9ec1ff5d6334/docs/zh/deploy/astrbot/btpanel.md) / [阅读页](https://docs.astrbot.app/deploy/astrbot/btpanel.html)
- [主动型能力](https://github.com/AstrBotDevs/AstrBot/blob/6914bc3aa61e14ca9a9c2cb37a0f9ec1ff5d6334/docs/zh/use/proactive-agent.md) / [阅读页](https://docs.astrbot.app/use/proactive-agent.html)
- [上下文压缩](https://github.com/AstrBotDevs/AstrBot/blob/6914bc3aa61e14ca9a9c2cb37a0f9ec1ff5d6334/docs/zh/use/context-compress.md) / [阅读页](https://docs.astrbot.app/use/context-compress.html)
- [插件开发](https://docs.astrbot.app/dev/star/plugin-new.html)
- [模型接入](https://docs.astrbot.app/providers/start.html)
- [QQ 官方机器人](https://docs.astrbot.app/platform/qqofficial.html)

## 怎么理解核对范围

本书区分几种材料：

- 原项目 README 和源码文档：用于确认已描述的接口、配置和限制。
- 原作者随笔与部署记录：用于说明经验，不当成控制实验。
- 教学示例与建议：帮助选择检查方式，不冒充真实模型结果。

本书没有比较所有模型，也没有在同一台生产服务器上验收所有插件组合。Markdown 图片与链接可检查，不等于 QQ 接入、模型表现和人物质量已经通过实际使用验证。
