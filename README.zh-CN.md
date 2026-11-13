# EthOS

[English](README.md) | [简体中文](README.zh-CN.md)

> 元宇宙应当是一个民有、**民治、民享**的世界。

EthOS 是一个基于 FluffOS/LPMud 驱动及 mudlib 的文字元宇宙原型框架。

浏览器终端通过 Python Web 服务连接 FluffOS 游戏世界，并接入 Ethereum 功能，例如 SIWE 钱包登录与玩家资产。

## 项目结构

| 路径 | 用途 |
| --- | --- |
| `src/ethos/` | Tornado Web 服务、WebSocket 代理、浏览器界面及 Web3 集成 |
| `lib/` | FluffOS mudlib：LPC 命令、房间、玩家与游戏守护进程 |
| `eth/` | Hardhat 项目，包含 Solidity 合约及部署任务 |
| `docs/` | 产品、协议及架构文档 |

## 本地运行

本地游戏需要三个服务：Ethereum JSON-RPC 节点、FluffOS 驱动和 Tornado Web 服务。请从仓库根目录开始，在不同终端中分别启动。

### 1. 准备项目

mudlib 使用 `lib/mudcore` 子模块，启动驱动前先初始化：

```sh
git submodule update --init lib/mudcore
```

安装 Python 3.10，并使用 uv 同步依赖：

```sh
uv python install 3.10
uv sync --python 3.10
```

依赖声明在 `pyproject.toml` 中，具体版本由 `uv.lock` 锁定。使用 `uv run` 即可在托管环境中运行 Python 命令，不需要手动激活 `.venv`。

### 2. 启动本地 Ethereum 节点并部署合约

```sh
cd eth
npm install
npx hardhat node
```

在另一个终端中，向该节点部署 `Player`。部署任务会先编译合约，再生成 Python 应用需要的 ABI 和合约地址文件：

```sh
cd eth
npx hardhat deploy --network localhost --contract Player
```

Web 服务在启动时加载 `Player`，因此 `src/ethos/static/abi/1337/` 下必须存在 `Player.json`。本地 Hardhat 节点重启后，链状态会重置；即使 JSON 文件仍存在，也必须重新部署合约。TemporalLoot 集成已停用。

### 3. 启动 FluffOS 驱动

Apple Silicon 机器需要 macOS 26 或更新版本，从仓库根目录运行：

```sh
./bin/driver.mac.arm64 lib/config.ini
```

`driver.mac.arm64` 是基于 `twinsant/fluffos` 提交 `3b4bc50049002ac8216cd2c04c9bf55adb0738ef` 构建的原生 ARM64 Release 版本。它动态链接 Homebrew 的 `mysql`、`openssl@3` 和 `icu4c@78`，运行机器需要安装这些库。

`driver.mac` 保留为 Intel macOS 预编译版本；Intel Mac 使用 `./bin/driver.mac lib/config.ini`。旧的 `driver.alpine` 仍保留，但生产部署使用 `driver.linux.x86_64`。

Linux x86-64 主机使用：

```sh
./bin/driver.linux.x86_64 lib/config.ini
```

`driver.linux.x86_64` 在主机 `t` 上构建，源码提交与 ARM64 版本相同。构建采用隔离的 Alpine 3.18.12 容器、GCC 12.2，以及 `Release`、`STATIC=ON`、`MARCH_NATIVE=OFF` 配置。产物为已去除调试符号的静态 ELF，并内嵌完整 ICU 字符数据，运行时不需要 Alpine 或另装 ICU 数据文件。验证通过了 767 个文件中的 12,781 项 LPC 检查；还在 CentOS 7/glibc 2.17 主机上脱离容器加载 EthOS mudlib，通过回环 WebSocket 获得 HTTP 101 升级响应及 `Getting Web3 DID` 登录提示。

构建目录、脚本、日志及产物保留在 `t` 的 `/root/projects/fluffos-build-3b4bc5004900/`，二进制位于 `output/driver.linux.x86_64`。本次构建没有安装或启动生产 EthOS 服务。

如果需要重新编译 ARM64 驱动，请先准备与本仓库同级的 `fluffos` 源码目录，并安装 CMake、Ninja 及相关依赖：

```sh
cmake -S ../fluffos -B ../fluffos/build-arm64 -G Ninja \
  -DCMAKE_BUILD_TYPE=Release -DCMAKE_OSX_ARCHITECTURES=arm64 \
  -DMARCH_NATIVE=OFF -DLWS_HAVE_PIPE2:INTERNAL=OFF \
  -DOPENSSL_ROOT_DIR=/opt/homebrew/opt/openssl@3 \
  -DICU_ROOT=/opt/homebrew/opt/icu4c@78
cmake --build ../fluffos/build-arm64 --target driver --parallel 6
ctest --test-dir ../fluffos/build-arm64 -R '^testsuite$' --output-on-failure
install -m 755 ../fluffos/build-arm64/src/driver bin/driver.mac.arm64
```

`LWS_HAVE_PIPE2=OFF` 让 libwebsockets 使用可移植的 `pipe()`：macOS 27 SDK 能检测到 `pipe2()`，但 macOS 26 不提供该 API。

### 4. 启动 Web 服务

从仓库根目录运行：

```sh
export ETHOS_COOKIE_SECRET="$(openssl rand -hex 32)"
PYTHONPATH=src ENDPOINT=http://127.0.0.1:8545 \
  uv run --python 3.10 python src/ethos/main.py \
  --debug --endpoint=http://127.0.0.1:8545
```

打开 **http://127.0.0.1:4003**，请保持使用这一主机名，因为 WebSocket 代理会检查请求来源。浏览器连接 Web 服务的 `4003` 端口，Web 服务再连接 FluffOS 的 `4001` 端口。

密钥至少需要 32 个字符，必须保密。若使用其他公开地址，设置 `ETHOS_ORIGIN` 为完整的协议和主机名，不带末尾斜杠。会话保存在内存中，12 小时后或服务重启后失效。玩家名称限 1–32 个小写英文字母、数字或下划线；认领须恰好支付 0.01 ETH，重复认领会回退。Player 所有权转移须由新所有者接受，且不能放弃所有权。名称注册仍存在交易抢跑风险。

窄屏下桌面窗口会换行，内容在桌面内部滚动，底部任务栏保持可见。可以拖动标题栏移动窗口，终端会自动适配容器大小。合约操作需要 MetaMask，但显示桌面不需要安装钱包。

### 当前限制

- Ropsten、Mumbai、Rinkeby 远端网络配置是可选的，只有设置对应 RPC URL 和私钥环境变量后才会加入 Hardhat 配置。本地 Hardhat 和 `localhost` 网络不需要远端凭据。
- 应用使用 Web3.py 5 时期的 API，`pyproject.toml` 将版本限制在兼容的 5.x 系列。
- 应用启动时需要可访问的 Ethereum JSON-RPC 端点，以及已经部署的 `Player` 合约。如果 `src/ethos/static/abi/<chain-id>/` 下缺少 `Player.json`，服务将无法启动。

WalletConnect 登录使用 V2 协议和官方中继。设置环境变量
`WALLETCONNECT_PROJECT_ID` 为 [Reown 控制台](https://dashboard.reown.com/)的项目 ID，
并在控制台将应用的访问源加入允许列表；未配置时 WalletConnect 登录会提示配置错误。
修改浏览器端集成后，重新生成并提交打包文件：

```sh
cd src/ethos/static
npm ci
npm run build
```

## 生产部署

`ops/deploy.sh` 将 `main` 分支部署到现有的 `twinsant.com` 腾讯云主机，访问地址为 `https://meta.twinsant.com`。它分别为 FluffOS 和 Tornado 配置 Supervisor 服务，安装独立的 Nginx HTTPS/WebSocket 虚拟主机，并在缺失时创建 `meta.twinsant.com` 的 DNS A 记录。已有且指向其他地址的 A 记录不会被覆盖。

部署前：

1. 将完整发布版本推送到 `origin/main`。脚本会拒绝未清理的工作区，以及尚未与当前 `origin/main` 一致的本地提交。
2. 配置具有 SSL 和 DNSPod 权限的 `tccli`，并确保目标主机能够克隆 `git@github.com:twinsant/ethos.git`。默认使用 `../twinsant.com/ops/ansible/inventory.ini`，可通过 `ANSIBLE_INVENTORY` 指定其他 inventory。
3. 从 `ops/production.env.example` 创建被 Git 忽略的 `ops/production.env`，填写 RPC 和密钥，并用 `chmod 600 ops/production.env` 限制文件权限。这是可信的 Shell 环境文件，请为值加引号。Infura 配置见下一节。
4. 将 `Player.json` 放入被 Git 忽略的 `ops/abi/<chain-id>/`，也可通过 `ETHOS_ABI_DIR` 指定另一个包含 `<chain-id>/` 子目录的根目录。文件必须包含非空的 `abi` 数组和已部署的 `address`。脚本会将文件复制到服务器，并在本地和远端分别验证链 ID 与合约字节码。开发链 `1337`、`31337` 会被拒绝。脚本不启动 Hardhat，也不部署合约；两台机器必须都能访问 RPC。
5. 在仓库根目录执行 `bash ops/deploy.sh`。脚本会先验证腾讯云证书 `bf3pwcJF` 并将其暂存到私密目录，再修改服务器配置。可通过 `ETHOS_CERTIFICATE_ID` 使用其他已签发证书；运行 `bash ops/deploy.sh --help` 查看支持的覆盖参数。

### 配置 Infura RPC

远端 Ethereum RPC 使用 Infura 时，在**执行部署的本地机器**上修改 **`ops/production.env`** 中的 `ENDPOINT` 即可。无需修改 `ops/deploy.sh`，也不要把 API Key 写入已跟踪的文件。脚本同样支持其他 HTTP(S) JSON-RPC 服务商。

从仓库根目录执行以下命令，创建配置文件并生成随机密钥；`cp -n` 不会覆盖已有生产配置：

```sh
cp -n ops/production.env.example ops/production.env
chmod 600 ops/production.env
openssl rand -hex 32
```

在 Infura 控制台选择要使用的网络，复制该网络的 HTTPS RPC 地址。如果使用 **Ethereum 主网**，编辑 `ops/production.env`：

```sh
ENDPOINT='https://mainnet.infura.io/v3/YOUR_INFURA_API_KEY'
WALLETCONNECT_PROJECT_ID='YOUR_PROJECT_ID'
ETHOS_COOKIE_SECRET='PASTE_THE_GENERATED_RANDOM_SECRET_HERE'
SLACK_SECRET=''
SLACK_CHANNEL='twinsant-com'
```

在本地替换 API Key 和 WalletConnect 项目 ID，并将刚生成的随机字符串填入 `ETHOS_COOKIE_SECRET`。不要公开 API Key 和 Cookie 密钥；该环境文件已被 Git 忽略，部署时会复制到服务器的 `/etc/ethos/ethos.env`。Slack 是可选功能，`SLACK_SECRET` 为空时禁用。

如果先使用 **Sepolia 测试网**，将端点改为：

```sh
ENDPOINT='https://sepolia.infura.io/v3/YOUR_INFURA_API_KEY'
```

| 网络 | Chain ID | 部署机器上的合约文件 |
| --- | --- | --- |
| Ethereum 主网 | `1` | `ops/abi/1/Player.json` |
| Sepolia | `11155111` | `ops/abi/11155111/Player.json` |

Infura 只提供 RPC 访问，**不会部署合约**。本地 Hardhat 上的合约不会自动出现在远端网络中。必须先在目标网络部署 `Player`，再把生成的 ABI/地址文件放到上表对应目录。使用 Hardhat 部署远端合约前，需要在 `eth/hardhat.config.js` 中配置对应网络；本地运行章节的命令只部署到 `localhost`。不要把钱包私钥写入 RPC 地址。

浏览器钱包必须切换到同一网络。主网部署合约和写入操作会消耗真实 ETH，Sepolia 则使用测试 ETH。修改 `ENDPOINT` 不会迁移合约或资产。本地部署机器和服务器都必须能访问选定的 Infura 端点，请留意 Infura 的访问限制及请求配额。

配置好端点、密钥与合约文件后，提交并推送发布代码（不要提交被忽略的配置文件），再运行 `bash ops/deploy.sh`。

### 运行环境与运维

部署脚本通过服务器已有的 Conda 安装，在 `/opt/ethos/.venv` 创建独立的 Python 3.10 环境。生产 Tornado 进程只监听 `127.0.0.1:4003`，FluffOS 监听 `127.0.0.1:4001`，Nginx 负责 TLS 终止以及 HTTP/WebSocket 反向代理。密钥配置以受限权限保存在 `/etc/ethos/ethos.env`，不会通过进程命令行传递。

目标主机必须已有 Nginx、Supervisor、Git、curl 和 `/root/miniconda3/bin/conda`，并允许 Ansible 使用 root 权限。内置静态 `bin/driver.linux.x86_64` 需要 Linux x86-64 主机；首次部署时，回环端口 `4001`、`4003` 必须空闲。Apple Silicon 驱动仅用于本地开发。服务用户可写入 mudlib 运行数据，部署会保留 `lib/data/` 和 `lib/log/`；请单独备份这些目录。

Supervisor 只更新或重启 `ethos-driver` 和 `ethos-web`。本地 HTTP 健康检查和驱动端口检查通过后，脚本安装 EthOS Nginx 配置，执行 `nginx -t` 并重新加载 Nginx。TLS 启用失败会恢复之前的 EthOS Nginx 文件。本地 HTTPS 主机名和证书检查通过后，才会创建缺失的 DNS A 记录。冲突的 A/CNAME/AAAA 记录不会被覆盖。腾讯云安全组需要开放 TCP `80`、`443`，无需向公网开放 `4001`、`4003`。

这不是原子化应用回滚：如果 Python 依赖安装或服务重启失败，可能需要重新部署之前的发布版本。脚本不会修改 FAPI 的 Conda 环境，也不会重启其他 Supervisor 服务。

续期时，先在腾讯云申请并验证新证书，再执行 `ETHOS_CERTIFICATE_ID=<新证书ID> bash ops/deploy.sh`。当前没有自动续期功能，免费证书有效期较短，请监控到期时间。

以下命令可在本地验证部署工具，不会修改生产环境：

```sh
bash -n ops/deploy.sh ops/run-web.sh
ansible-playbook -i ../twinsant.com/ops/ansible/inventory.ini ops/ansible/deploy.yml --syntax-check
uv run --python 3.10 python -m unittest discover -s ops/tests -v
```

## 截图

<img width="770" alt="EthOS 界面截图" src="https://user-images.githubusercontent.com/299586/153534242-c25e8e25-bdda-4c32-9cc2-4e21d7c4ca2e.png">

## 架构

<img width="827" alt="EthOS 架构图" src="https://user-images.githubusercontent.com/299586/156308820-82483660-df6a-4771-8e96-254890739bbf.png">

## 路线图

- 阶段 1：身份、社交、多样性、数字经济。
- 阶段 2：任意接入、文明、低摩擦。
- 阶段 3：沉浸体验。

### 1. 身份（区块链 NFT），2022.1 已完成

- [SIWE/EIP-4361](https://login.xyz/)
- [Particle Auth](https://particle.network/auth-introduction.html)
- ENS
  - [FluffOS Socket EFuns](https://www.fluffos.info/concepts/general/socket_efuns.html)
- [ENS Profile](https://medium.com/the-ethereum-name-service/step-by-step-guide-to-setting-an-nft-as-your-ens-profile-avatar-3562d39567fc)

### 2. 社交（游戏与教育）

- Ethereum Friend List（EFL）
- Ethereum Message System（EMS）
- 参考阅读：Human Evolution。

### 3. 沉浸体验（NLP/AI + VR/AR/XR 交互）

- [MagicaVoxel](http://ephtracy.github.io/)
- 参考阅读：Hooked、Designing with the Mind in Mind、The Element of User Experience、Deep Learning。

### 4. 低摩擦

- 5G/6G 市场份额。
  - 2021 年 2 月：中国移动 18%、中国电信 29.3%、中国联通 27.6%。
  - 2022 年。
  - 2023 年：33.3%。
  - 2024 年。
  - 2025 年：50% 临界点。

### 5. 多样性（AIGC + UGC + PGC）

- [ai.com](https://ai.com)
- [Loot 文档](https://docs.loot.foundation/)
- 巫师角色。
- [LPC](https://www.fluffos.info/concepts/general/lpc.html) 编辑器。
  - [预处理器](https://www.fluffos.info/concepts/general/preprocessor.html)
  - [LPC 中文教程](https://bbs.mud.ren/threads/3)
- 参考资料：[Linden Scripting Language](http://wiki.secondlife.com/wiki/LSL_Portal)。

### 6. 任意接入（物联网）

- Discord
- iOS App
- Android App
- H5

### 7. 数字经济（带代币的区块链）

- ERC20 Token/ERC1155
- 交易市场房间

模型：

- 生命值（最小值到最大值）：魔法值、智商、情商。
- 技能点与经验值：攻击力对应力量，防御力对应护甲。
- 工分。

参考阅读：

- Sapiens: A Brief History of Humankind
- Numbers and the Making of Us
- Scale
- Money Changes Everything
- The Origin of Wealth: Evolution, Complexity, and the Radical Remaking of Economics
- The Great Game: The Emergence of Wall Street as a World Power
- Money Mischief
- [Bitcoin: A Peer-to-Peer Electronic Cash System](https://bitcoin.org/en/bitcoin-paper)
- [工分制的制度经济学分析](https://www.cuhk.edu.hk/ics/21c/media/articles/c131-201104022.pdf)
- [A Guide to the Dungeons of Doom](https://docs.freebsd.org/44doc/usd/30.rogue/paper.pdf)

### 8. 文明（复杂网络）

- DAO

参考阅读：

- [The Nature of the Firm](https://onlinelibrary.wiley.com/doi/full/10.1111/j.1468-0335.1937.tb00002.x)
- The Crowd: A Study of the Popular Mind
- Truth
- The Timeless Way of Building
- Favor and Face: Power Game of Chinese
- The Republic of Pirates
- 《中国历代政治得失》

## 许可证

参见 [FluffOS Copyright](https://github.com/fluffos/fluffos/blob/master/Copyright)。

LPC 背景：[LPMud](https://en.wikipedia.org/wiki/LPMud)。
