# 7. 实例：AstrBot + NapCat + 宝塔

[上一章](06-models.md) · [目录](../README.md) · [下一章：记忆与工具](08-memory-and-tools.md)

这一章先完成一件事：**QQ 发来一条消息，AstrBot 调用模型，再把回答送回 QQ。**

先不用装记忆、表情、防抖和主动消息插件。基础链路跑通以后，才知道新增功能带来了什么变化。

本章以 Linux 服务器上的宝塔 Docker 环境为例，使用 AstrBot + NapCat。LLBot 用户可以沿用前面的职责划分，但安装与协议端配置应跟随 [LLBot 原项目](https://github.com/LLOneBot/LuckyLilliaBot)，不要照抄 NapCat 的容器路径。

## 先确定访问方式

旧的[宝塔部署文章](../articles/astrbot-napcat-baota-deploy.md)保留了完整操作截图，但其中直接映射多个端口、建议先留空 token、使用 `latest` 的做法，不作为这里的默认方案。截图用来认页面和字段，不要求复制图片里的地址、凭据或全部配置。

本章的容器与端口分工：

- 两个容器在同一台服务器、同一 Docker 网络。
- NapCat 用容器服务名连接 AstrBot，不让这段通信绕公网。
- AstrBot 管理页使用宿主机 `6185`，NapCat 管理页使用宿主机 `6099`；模板默认仅绑定回环地址，要直接通过服务器 IP 访问时再按下文调整。
- AstrBot 的 `6199` 是 OneBot 反向 WebSocket 服务端口，**不是管理页面**；同网络容器可以连接，不需要把它发布到宿主机。
- OneBot 连接两端设置一致的非空随机 token。

宝塔本来就有图形化的 Docker、编排、容器日志和安全设置，本章以页面操作为主。管理页可以从可信内网或 VPN 使用 `服务器IP:端口` 打开；如果只能走公网，先为日常管理准备 HTTPS 的受限入口。SSH 隧道只是可选的访问方法，不是安装 AstrBot 的前置要求。

| 端口 | 本例用途 | 模板的初始映射 |
| --- | --- | --- |
| `6185` | AstrBot 管理页面 | 宿主机回环地址；按访问方式决定是否调整 |
| `6099` | NapCat 管理页面 | 宿主机回环地址；按访问方式决定是否调整 |
| `6199` | AstrBot OneBot v11 服务 | 仅供同网络容器访问，不发布到宿主机公网 |
| `3000 / 3001` | NapCat 可选服务 | 本例不用，不映射 |

从外部打开管理页，要分别检查三件事：**云服务器安全组或上游防火墙**是否允许你的来源 IP，**宝塔“安全”中管理的服务器系统防火墙**是否允许相应访问，以及 **Docker 编排是否将这个端口映射到外部可达的宿主机地址**。宝塔页面管理的规则通常就是服务器上的防火墙规则，不一定还有一套独立的“面板防火墙”。[Docker 官方文档](https://docs.docker.com/engine/install/ubuntu/#firewall-limitations)提醒，发布的端口可能绕过 ufw/firewalld 的规则，不能只凭宝塔页面显示“已禁止”就认定外网不可访问；还要从另一条网络实际检查。不要用 `ALL` 放行代替排查，也别把宝塔面板自身的管理端口与容器端口混为一谈。

## 准备好这些东西

你需要一台能运行所选镜像的服务器、可登录的宝塔面板、Docker、用于测试的 QQ 账号，以及一个可用模型服务。

个人号协议端不能保证账号安全或长期可用。先了解项目说明和 QQ 平台要求；不要将重要账号与未经验证的自动化绑定。模型服务也可能收到聊天文本与图片，需要自行接受相应的数据处理方式。

先不要填写任何真实凭据到公开笔记。之后备份数据时，也要把聊天和登录状态当作敏感文件。

## 第一步：准备 Docker

在宝塔的 Docker 页面确认环境能启动。AstrBot 已提供宝塔应用商店安装方式，见[官方宝塔文档](https://docs.astrbot.app/deploy/astrbot/btpanel.html)。

![宝塔中搜索 AstrBot 的历史界面](../assets/blog-assets/astrbot-napcat-baota/05-search-astrbot.webp)

有两条安装路线：

1. 在应用商店安装 AstrBot，再手动创建 NapCat，并给两个容器设置一致的网络。
2. 在 Docker 编排页面一起创建两个服务。

为了把网络、端口和数据目录讲清楚，下面选第二条。**不要再同时运行应用商店里另一份同端口 AstrBot。** 已经安装好的用户，可检查现有配置，不必重建。

## 第二步：在宝塔编排中启动两个容器

仓库提供 [compose.yaml](../examples/astrbot-napcat/compose.yaml) 与 [.env.example](../examples/astrbot-napcat/.env.example)。这是基于 [NapCat-Docker 的 AstrBot 模板](https://github.com/NapNeko/NapCat-Docker/blob/f0599fb2eef4e9007aed72501849e2ca3eeaccdf/compose/astrbot.yml)整理的手动连接示例，没有开启其自动模板化 `MODE=astrbot`。

在宝塔中新建编排项目，把这两个文件的内容分别放入编排与环境变量配置。镜像项没有内置 `latest`：请从 [AstrBot](https://github.com/AstrBotDevs/AstrBot) 和 [NapCat-Docker](https://github.com/NapNeko/NapCat-Docker) 确认当前可用镜像，填写你实际选择的固定标签或摘要，并记录下来。

镜像值使用完整形式，例如 `仓库名:固定标签` 或 `仓库名@sha256:实际摘要`；这两段只是格式说明，不是可运行的镜像地址。若宝塔的编排界面不支持所用的环境变量展开方式，就在自己的编排中填入已选好的完整镜像值。不要把 `.env.example` 文件名原样当作自动加载的 `.env`。

管理页的绑定地址由 `ADMIN_BIND_IP` 控制。模板默认值 `127.0.0.1` 适合在服务器本机通过 HTTPS 反向代理访问，或通过可选的本地隧道访问；此时外部的 `服务器IP:6185` 不会直通容器。要在**可信内网或 VPN**直接打开 `服务器IP:6185` 和 `服务器IP:6099/webui`，先在云安全组限定来源，核对宝塔的系统防火墙，再把 `ADMIN_BIND_IP` 改成该内网可达的绑定地址或 `0.0.0.0`，启动后从预期网络与非预期网络各检查一次。如果服务器同时有公网地址，`0.0.0.0` 也会绑定公网接口，不能只看内网测试通过。

若只能从公网管理，建议保持默认回环绑定，用宝塔网站的反向代理和证书为管理页建立受限 HTTPS 入口，NapCat 页面也只对受信任来源开放。公网直接访问 `http://服务器IP:6185` 虽然技术上可行，但明文 HTTP 不会保护登录凭据与 API Key，不能因为设置了来源 IP 白名单就当作加密连接。

已有 Docker CLI 时，也可以在存放这两个文件的服务器项目目录执行：

```sh
docker compose --env-file .env config --quiet
docker compose --env-file .env up -d
docker compose ps
```

这里 `.env` 是你在服务器上填好的实际配置，不是仓库中的 `.env.example`。缺少镜像值时，模板会拒绝启动，而不是偷偷使用一个未知版本。本书没有在你的服务器上实际运行这些命令。

模板持久化了：

| 宿主机目录 | 用途 |
| --- | --- |
| `data/` | AstrBot 数据；同时挂到 NapCat 的相同 `/AstrBot/data` 路径，支持按这一方式共享媒体文件 |
| `napcat/config/` | NapCat 配置 |
| `ntqq/` | QQ 登录相关数据 |

这些目录相对于编排项目位置创建，不要删除后期待系统仍记得配置。不要把它们提交到 Git。

如果服务未启动，先看日志和挂载权限。不要为了省事对整个数据目录开放任意写入权限。

## 第三步：打开各自的管理页面

在宝塔的 Docker 容器列表确认两个容器都在运行，查看映射端口和日志。若已经按上一步配置了可信内网或 VPN 的 IP 直连，从有访问权限的设备打开：

```text
http://服务器IP:6185
http://服务器IP:6099/webui
```

地址中的 `服务器IP` 是这台管理设备可达的服务器地址，不是容器地址。直接在浏览器输入 `http://服务器IP:6199` 不会打开管理页；那是 OneBot 连接使用的端口，本例根本没有把它映射出来。如果用 HTTPS 反向代理，则打开你在宝塔网站里配置好的 HTTPS 地址，而不是上面这两个明文 HTTP 地址。

已经通过 SSH 管理服务器、但不方便配置另一种受限访问方式的用户，也可以**选择**维持回环绑定，建立本地隧道：

```sh
ssh -N -L 16185:127.0.0.1:6185 -L 16099:127.0.0.1:6099 管理账号@服务器地址
```

这时在本机打开 `http://127.0.0.1:16185` 和 `http://127.0.0.1:16099/webui`。隧道终端需要保持连接；本机端口被占用时可改 `16185`、`16099`，并同步修改浏览器地址。这条路径不要求在公网发布 `6185` 或 `6099`。

![AstrBot 欢迎页的历史界面](../assets/blog-assets/astrbot-napcat-baota/11-astrbot-welcome.webp)

先完成 AstrBot 的实际初始化与账户设置，不在教程里依赖永久有效的默认密码。NapCat 的登录 token 按当前容器日志和官方说明获取，不使用截图里的值。

管理页打不开，先核对选的是 IP 直连、反向代理还是隧道，再看绑定地址、Docker 映射和相应网络规则。不要为了省事长期公开裸露管理页。

不确定 NapCat 的登录 token 在哪里时，可以在宝塔打开该容器日志；CLI 对应命令是 `docker compose logs napcat`。日志可能包含登录链接和凭据，查看后不要整段复制到公开求助帖。

## 第四步：登录 QQ 协议端

打开 NapCat 页面，按当前版本的提示登录测试 QQ。扫码、验证码和设备确认应由账号持有者完成。

![NapCat 基础信息页的历史界面](../assets/blog-assets/astrbot-napcat-baota/15-napcat-dashboard.webp)

二维码、登录状态与 WebUI token 都不要发进群或公开 Issue。风控或验证失败时，按项目及平台提示处理，不连续盲目重试。

这一步只确认 NapCat 已登录 QQ，还没有证明 AstrBot 已连接。

## 第五步：先把模型单独测通

在 AstrBot 的模型提供商页面，按服务商说明配置接口地址、API Key 和实际模型 ID，再选择要用于这个配置或会话的聊天模型。菜单名称可能随版本变化。

![AstrBot 模型配置入口的历史界面](../assets/blog-assets/astrbot-napcat-baota/16-astrbot-model-entry.webp)

本书不要求特定服务商，也不把旧截图里的模型名当成当前可用列表。特别留意接口地址的路径是否已经包含版本前缀；按服务商与 AstrBot 文档匹配，不凭猜测反复添加 `/v1`。

先在 AstrBot 自带聊天入口发一句普通消息。失败时检查凭据、余额、模型 ID、网络和日志。这时还不涉及 QQ，便于把问题缩小。

原生看图、工具调用与纯文本对话是不同能力。第一句正常回复，不代表它们已经全部配置好。

## 第六步：让 AstrBot 等待 OneBot 连接

在 AstrBot 的“机器人”管理里新增 OneBot v11 实例：

| 项目 | 本例设置 |
| --- | --- |
| 实例 ID | 自己能识别的名字，例如 `qq-napcat` |
| 启用 | 开启 |
| 反向 WebSocket 主机地址 | `0.0.0.0`，使容器内服务可被同网络容器访问 |
| 反向 WebSocket 端口 | `6199` |
| 反向 WebSocket Token | 为这条连接生成的随机 token |

这里的 `0.0.0.0` 是监听地址，不是让 NapCat 连接的目标地址；本例也没有把 `6199` 发布到服务器公网。

![AstrBot OneBot v11 表单的历史界面](../assets/blog-assets/astrbot-napcat-baota/24-create-onebot-robot.webp)

图中 token 字段可能为空。本书实例应填入非空值，随后在 NapCat 的 OneBot 客户端配置中填同一个值。

**OneBot token 与 NapCat WebUI 登录 token 用途不同，不需要复用。** 上面的 `.env` 也不会自动替你配置这两个页面的认证信息。

## 第七步：让 NapCat 连接 AstrBot

在 NapCat 网络配置中新增并启用 WebSocket 客户端，目标地址填写：

```text
ws://astrbot:6199/ws
```

这里的 `astrbot` 来自编排里的服务名，两者处在同一网络，所以可以解析。填写匹配的 OneBot token 并保存。

![NapCat 新建 WebSocket 客户端的历史界面](../assets/blog-assets/astrbot-napcat-baota/25-create-napcat-ws-client.webp)

回到 AstrBot 日志，查找适配器已连接的记录。不要仅凭 NapCat 页面显示“已登录 QQ”，就认定反向连接完成。

如果两者部署在不同机器，本章这个地址不适用。那需要重新设计可达地址、认证和受保护的传输方式；不能直接把 `6199` 无认证开放到公网。

## 第八步：从 QQ 走一遍

用另一个 QQ 账号给机器人发一句“你好”，按顺序看：

1. 协议端是否收到事件。
2. AstrBot 是否收到对应私聊。
3. 是否调用了你选择的模型。
4. 模型是否返回可见正文或正确的发送结果。
5. QQ 是否收到回复。

![原部署文章中的 QQ 回复示例](../assets/blog-assets/astrbot-napcat-baota/28-qq-bot-reply.webp)

这张图只用来说明“QQ 收到回复”这一结果，不是本书对台词、气泡数量或人物表现的评分标准，也不是本次重新部署的实测截图。

再发一张普通图片，检查模型实际是否能处理。图片失败时要区分模型能力、文件可达性和媒体传递方式，不要立即给人设加“你可以看图”。

## 第九步：保存一个能恢复的起点

在继续装插件前，记录 AstrBot、NapCat、镜像、模型 ID 和当前配置。导出必要设置，在不会被公开访问的位置备份数据。

数据存储正在写入时，直接拷贝不一定形成一致的备份；使用项目支持的导出方式，或在合适的维护窗口停止相关服务再备份。至少知道恢复时要放回哪些目录，以及镜像升级后是否涉及数据兼容。

现在才适合逐个加入第 3、4 章的能力。不要一口气安装所有拟人化插件，否则第一次异常出现时，很难知道是谁改了输入或抢了发送。

## 快速排错

| 现象 | 先看 |
| --- | --- |
| 管理页打不开 | URL 是否用了 `6185`/`6099` 而非 `6199`；容器状态、`ADMIN_BIND_IP`、映射、云安全组与宝塔防火墙；选择隧道时检查连接 |
| QQ 登录正常，AstrBot 没事件 | OneBot 实例启用状态、客户端目标地址、两端 token |
| AstrBot 有事件，但模型失败 | 实际模型、凭据、余额、接口路径、服务商返回 |
| 文字正常，图片不行 | 模型图片能力、共享路径、协议端文件读取、发送返回 |
| 重启后需要重新配置 | 数据挂载是否指向原目录、权限是否正确 |

参考：[AstrBot 宝塔部署](https://docs.astrbot.app/deploy/astrbot/btpanel.html)、[OneBot v11 接入](https://docs.astrbot.app/platform/aiocqhttp.html)、[NapCat-Docker](https://github.com/NapNeko/NapCat-Docker)、[原图文教程](../articles/astrbot-napcat-baota-deploy.md)。本书的编排示例尚未完成真实 QQ 登录与收发验收。
