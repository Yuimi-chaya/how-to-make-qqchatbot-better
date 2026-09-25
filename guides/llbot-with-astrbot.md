# 用 LLBot 官方脚本接入 AstrBot

[返回目录](../README.md) · [链路说明](../chapters/02-the-stack.md) · [NapCat 安装实例](../chapters/07-astrbot-deployment.md)

这是一条与 NapCat 并列的接入路线：**LLBot 连接 QQ，AstrBot 接收 OneBot v11 事件并调用聊天模型**。下文只讲 Linux 服务器上的官方 Docker 安装脚本和 AstrBot 的反向 WebSocket 连接；LLBot 不替你配置模型与人设，也不需要与 NapCat 同时登录同一个测试账号。

操作以 [LuckyLilliaBot 官方脚本的固定提交](https://github.com/LLOneBot/LuckyLilliaBot/blob/9f374f6442b6c38a95841fc1d472cf6d8ea6149e/script/install-llbot-docker.sh)为准。脚本会写入真实凭据、生成 `docker-compose.yml` 和配置文件，还可能立即启动容器；先读完以下选择与风险，再在你自己的服务器执行。未在本书环境中登录 QQ 或实际运行该脚本。

## 准备一个单独目录

先在宝塔确认 Docker 和 Compose 可用。可以按 [AstrBot 官方宝塔教程](https://docs.astrbot.app/deploy/astrbot/btpanel.html)在应用商店安装 AstrBot；若沿用[第 7 章的双服务编排](../chapters/07-astrbot-deployment.md)，只启动其中的 `astrbot` 服务，不要再让 `napcat` 用同一个测试号连接。若编排页面不能单独启动服务，在该项目目录使用 `docker compose up -d astrbot`；已经启用 NapCat 的，切换账号接入前先确认它不再处理同一个 QQ 号。然后在 AstrBot 新建并启用 OneBot v11 实例，容器内监听 `0.0.0.0:6199`。到宝塔的 Docker 网络页面记下 AstrBot 容器的实际网络与可解析名称：应用商店安装时不一定叫 `astrbot`。准备你有权使用的 QQ 测试号和从脚本提示的[授权入口](https://auth.luckylillia.com)取得的 LLBot **Auth Token**。它只用于 LLBot 登录鉴权，不是 AstrBot 的 OneBot token，也不是 LLBot WebUI 密码。

脚本会在**当前目录**写文件，已有同名 `docker-compose.yml` 可能被覆盖。先用宝塔文件管理器新建一个专用空目录，或在服务器终端进入该目录。下面是固定版本的下载与启动向导示例；`less` 用来先检查脚本，确认后再运行：

```sh
curl -fL -o install-llbot-docker.sh \
  'https://raw.githubusercontent.com/LLOneBot/LuckyLilliaBot/9f374f6442b6c38a95841fc1d472cf6d8ea6149e/script/install-llbot-docker.sh'
less install-llbot-docker.sh
sudo bash install-llbot-docker.sh
```

这些命令仅供在服务器上操作的读者使用，本书没有替你执行。不要把未知来源的 `curl | bash` 当作常规安装步骤。官方脚本在向导后半段检查 root 权限与 Docker；缺少任一条件时仍可能已经写出配置，但不会替你成功启动容器。

## 按向导选择

脚本的提问顺序如下。想先接通 AstrBot，可以走“无头 + 现在配置 + OneBot 11 WebSocket 客户端”这条最短路线：

| 提问 | 本例怎样选择 | 这一步实际决定什么 |
| --- | --- | --- |
| `Auth Token`、QQ 号 | 填自己的有效 token 与纯数字 QQ 号 | 鉴权与要登录的账号；脚本只检查 token 非空，不负责验证它可用 |
| 连接模式 `1/2` | `1` 无头；需要 QQ 客户端容器再选 `2` PMHQ 有头 | `1` 生成单个 `llbot` 服务；`2` 另起 `pmhq`，占更多资源且生成配置含 `privileged: true` |
| 配置方式 `1/2` | `1` 现在配置 | `2` 只准备 WebUI，OneBot 连接要等启动后到 WebUI 里再配 |
| WebUI 密码与端口 | 设置非空英文数字密码；端口默认 `3080` | 密码写入 `llbot_config/webui_token.txt`；这不是 OneBot token |
| 启用协议 | 选 `1` OneBot 11 | `2` Milky、`3` Satori 也可多选，但本例不需要 |
| OneBot 11 连接类型 | 选 `2` WebSocket 客户端 | 让 LLBot 主动连 AstrBot；`1` 是让 LLBot 自己当服务端，不是本例 |
| WebSocket URL 与 Token | 本书 Compose 用 `ws://astrbot:6199/ws`；其他安装按共享网络里的实际名称填写；Token 填与 AstrBot 端一致的非空随机值 | 此处脚本允许 Token 留空，但本例不留空；网络接通后这个 URL 才能解析 |
| 继续配置连接 | 选 `0` 完成 | 别误选服务端、HTTP 或 WebHook 来替代已有客户端 |
| Docker 镜像源 | 无下载问题可选 `n` | 选 `y` 时脚本检测其列出的镜像源；失败可能回退官方源及 `latest` |
| 是否立即启动 | 先选 `n` | 先检查生成的文件、网络和端口，再自己启动 |

若选 PMHQ，账号由 `pmhq` 容器处理，脚本会把 Auth Token 放入其 Compose 环境变量；无头模式则会写入 `llbot_config/auth_token.txt`。镜像标签通常按 npm 最新版本查询生成，失败时也可能退回 `latest`。需要可重复部署就先记录并核对实际镜像标签，再决定是否启动。

脚本会递归给 `llbot_config` 设置 `777` 权限，并在终端回显 WebUI 密码；生成的 Compose 还会默认把 WebUI 端口按 `3080:3080` 这样的方式发布。**这些是脚本现状，不是本书推荐的凭据权限或公网访问方式。** 别在共享账号机器或公开网站目录运行向导，不要提交配置目录、终端记录、二维码或登录状态。检查容器所需的实际读写用户后再收紧目录权限；不了解权限时别直接照搬一个可能令容器不能写入的 `chmod` 数字。

## 先让两个容器处在同一网络

若沿用本书的 AstrBot Compose，它有名为 `bot` 的网络定义；Docker 里的**实际网络名**通常带项目名前缀。应用商店安装的网络名可能完全不同。LLBot 安装脚本单独生成另一个 Compose 项目，两个容器即使在同一台服务器，也未必能互相解析名称。到宝塔的 Docker 网络页面看 AstrBot 容器连在哪个网络，再让 `llbot` 也加入那个用户自定义网络；或者在两个 Compose 文件里显式使用同一个外部网络。

若要让脚本生成的连接在容器重建后仍保持，不只是在面板里临时连接一次网络，还应把共享网络写进 LLBot 的 Compose。下面是**片段**，不是可以直接覆盖整份 `docker-compose.yml` 的成品。将网络名替换为宝塔里看到的真实名字：

```yaml
services:
  llbot:
    # 保留脚本生成的 image、environment、volumes 等其他字段
    networks:
      - astrbot_shared

networks:
  astrbot_shared:
    external: true
    name: 实际的AstrBot网络名
```

如果选了 PMHQ，有头模式的 `llbot` 原本已经加入 `app_network`。这时在它的 `networks` 列表中**保留 `app_network`，再加 `astrbot_shared`**，不要把 `pmhq` 与 `llbot` 之间的原有网络删掉。宝塔面板的“连接网络”操作可以用于临时核对；容器被更新或重建后，仍以 Compose 声明为准。

在同一用户自定义网络中，LLBot 可用 `ws://astrbot:6199/ws` 连接 AstrBot；这里的 `astrbot` 是本书 Compose 的服务名。如果你的 AstrBot 实际服务名不同，要用共享网络里能解析到它的名称。也可以临时用 `ws://<AstrBot容器IP>:6199/ws` 排查，但容器 IP 会在重建后变化，不适合写成长期配置。**这里的 IP 是 Docker 网络里的容器 IP，不是服务器公网 IP**；本例的 `6199` 不需要对宿主机发布。AstrBot 端要监听容器内可达的地址，两端 OneBot token 要相同。

## 检查访问范围，再启动

脚本生成的 WebUI 端口映射如果不需要远程直连，可在宝塔的 Compose 编辑页改为 `127.0.0.1:3080:3080`，再走受限 HTTPS 入口或隧道。如果使用可信内网/VPN 的服务器 IP 访问，就按[前一章的三层网络检查](../chapters/07-astrbot-deployment.md#先确定访问方式)限制来源并实测；不要把明文 WebUI 长期裸露到公网。`3080` 是 LLBot 管理页面，`6199` 是 AstrBot 的 OneBot 服务端，不可互换。

确认 `docker-compose.yml`、`llbot_config/`、镜像标签、共享网络和端口后，在宝塔编排里启动，或者在脚本生成文件所在目录执行：

```sh
sudo docker compose config
sudo docker compose up -d
sudo docker compose ps
sudo docker compose logs llbot
```

扫码与账号确认按 LLBot WebUI 的实际提示完成。WebUI 显示 QQ 已登录，只证明协议端登录；回到 AstrBot 看 OneBot 适配器是否连上，再用另一个 QQ 发消息做端到端测试。若 LLBot 连接失败，依次查服务名/容器 IP、两个容器是否真在同一网络、AstrBot 监听地址、`/ws` 路径和两端 Token。不要为了排错把 `6199` 无认证地开放到公网。

`docker compose config` 和容器日志可能显示凭据或登录二维码，不要整段贴到公开求助帖。收发成功后记录脚本与镜像版本，备份配置和登录数据时同样按敏感文件处理。

脚本、WebUI 和 QQ 客户端会更新。这里列的是所引固定版本的实际选项，不保证未来的菜单、镜像和自动登录行为完全一样；从原项目文档与脚本确认差异后再操作。

---

[上篇：QQ 聊天背后的整条链路](../chapters/02-the-stack.md) · [目录](../README.md) · [下篇：NapCat 安装实例](../chapters/07-astrbot-deployment.md)
