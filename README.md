# EthOS

[English](README.md) | [简体中文](README.zh-CN.md)

> Metaverse shall be a world of the people, **by the people and for the people**.

A prototype framework for building text-based metaverses, based on the FluffOS/LPMud driver and mudlibs.

EthOS connects a browser-based terminal to a FluffOS game world, with a Python web server bridging the game to Ethereum features such as SIWE sign-in and player assets.

## Project layout

| Path | Purpose |
| --- | --- |
| `src/ethos/` | Tornado web server, WebSocket proxy, browser UI, and Web3 integrations |
| `lib/` | FluffOS mudlib: LPC commands, rooms, players, and game daemons |
| `eth/` | Hardhat project containing Solidity contracts and deployment tasks |
| `docs/` | Product, protocol, and architecture documentation |

## How to run locally

The local game uses three services: a local Ethereum JSON-RPC node, the FluffOS driver, and the Tornado web server. Start each in a separate terminal from the repository root.

### 1. Prepare the project

The mudlib uses the `lib/mudcore` submodule. Initialize it before starting the driver:

```sh
git submodule update --init lib/mudcore
```

Install Python 3.10 and sync the project dependencies with uv:

```sh
uv python install 3.10
uv sync --python 3.10
```

Dependencies are declared in `pyproject.toml` and pinned in `uv.lock`. Use `uv run` to run Python commands inside the managed environment; activating `.venv` manually is not required.

### 2. Start a local Ethereum node and deploy the contracts

```sh
cd eth
npm install
npx hardhat node
```

In another terminal, deploy `Player` to that node. The task compiles the contract, then writes the ABI and address file used by the Python app:

```sh
cd eth
npx hardhat deploy --network localhost --contract Player
```

The web server loads `Player` at startup and requires `Player.json` under `src/ethos/static/abi/1337/`. After restarting the local Hardhat node, redeploy it: the chain state is reset, even if the JSON file still exists. TemporalLoot integration is disabled.

### 3. Start the FluffOS driver

From the repository root, on Apple Silicon (macOS 26 or later):

```sh
./bin/driver.mac.arm64 lib/config.ini
```

`driver.mac.arm64` is a native ARM64 Release build of `twinsant/fluffos` at commit `3b4bc50049002ac8216cd2c04c9bf55adb0738ef`. It dynamically links Homebrew's `mysql`, `openssl@3`, and `icu4c@78`; these libraries must be installed on the machine running it.

`driver.mac` remains the prebuilt Intel macOS executable; run `./bin/driver.mac lib/config.ini` on Intel Macs. The older `driver.alpine` is retained, but production deployment uses `driver.linux.x86_64`.

On Linux x86-64:

```sh
./bin/driver.linux.x86_64 lib/config.ini
```

`driver.linux.x86_64` was built on host `t` from the same FluffOS commit as the ARM64 build, using an isolated Alpine 3.18.12 container, GCC 12.2, and `Release`, `STATIC=ON`, `MARCH_NATIVE=OFF`. It is a stripped, statically linked ELF executable with full ICU character data embedded, so it does not require Alpine or separately installed ICU data on the runtime host. Validation passed all 12,781 LPC checks across 767 files, plus a native CentOS 7/glibc 2.17 smoke test that loaded the EthOS mudlib, upgraded a loopback WebSocket to HTTP 101, and received the `Getting Web3 DID` login prompt.

The build workspace, recipe, logs, and output remain on `t` under `/root/projects/fluffos-build-3b4bc5004900/`; the binary is in `output/driver.linux.x86_64`. This build did not install or start production EthOS services.

To rebuild the ARM64 driver from a sibling `fluffos` checkout with CMake, Ninja, and the dependencies installed:

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

`LWS_HAVE_PIPE2=OFF` keeps libwebsockets on the portable `pipe()` path: the macOS 27 SDK detects `pipe2()`, but that API is unavailable on macOS 26.

### 4. Start the web server

From the repository root:

```sh
export ETHOS_COOKIE_SECRET="$(openssl rand -hex 32)"
PYTHONPATH=src ENDPOINT=http://127.0.0.1:8545 \
  uv run --python 3.10 python src/ethos/main.py \
  --debug --endpoint=http://127.0.0.1:8545
```

Open **http://127.0.0.1:4003** (use this exact hostname because the WebSocket proxy checks the origin). The browser connects to the web server on port `4003`; the web server connects to FluffOS on port `4001`.

The secret must be at least 32 characters and kept private. For a different public origin set `ETHOS_ORIGIN` to the exact scheme and host, without a trailing slash. Sessions are held in memory and expire after 12 hours or a server restart. Player names are 1–32 lowercase ASCII letters, digits or underscores; claims require exactly 0.01 ETH and repeat claims revert. Player ownership transfers require acceptance by the new owner; ownership cannot be renounced. Name registration remains susceptible to transaction front-running.

The desktop windows wrap on narrow screens and scroll inside the desktop, keeping the bottom taskbar visible. Drag windows by their title bars; the terminal automatically fits its container. MetaMask is required for its contract actions, but not for rendering the desktop.

### Current setup limitations

- Remote Ropsten, Mumbai, and Rinkeby networks are optional and only added when their RPC URL and private key environment variables are set. The local Hardhat and `localhost` networks work without remote credentials.
- The app uses Web3.py 5-era APIs; `pyproject.toml` constrains Web3.py to the compatible 5.x series.
- The app requires a reachable Ethereum JSON-RPC endpoint and a deployed `Player` contract at startup. Without `Player.json` under `src/ethos/static/abi/<chain-id>/`, the server will not start.

## Production deployment

`ops/deploy.sh` deploys the `main` branch to the existing `twinsant.com` Tencent Cloud host as `https://meta.twinsant.com`. It installs the FluffOS driver and Tornado app as separate Supervisor programs, configures an independent Nginx virtual host for HTTPS and WebSockets, and creates the `meta.twinsant.com` DNS A record if it does not exist. An existing A record pointing elsewhere is never overwritten.

Before deploying:

1. Push the complete release to `origin/main`. The script refuses to deploy a dirty worktree or a local commit that is not the current `origin/main`.
2. Configure `tccli` with access to SSL and DNSPod, and make sure the target inventory host can clone `git@github.com:twinsant/ethos.git`. By default the script uses `../twinsant.com/ops/ansible/inventory.ini`; set `ANSIBLE_INVENTORY` to use a different inventory.
3. Copy and edit the ignored production environment file:

   ```sh
   cp ops/production.env.example ops/production.env
   openssl rand -hex 32
   ```

   Set `ENDPOINT` to the production HTTP(S) JSON-RPC endpoint, use the generated value for `ETHOS_COOKIE_SECRET`, and optionally set `SLACK_SECRET`. This is a trusted shell environment file; quote values and restrict its permissions with `chmod 600 ops/production.env`.
4. Put `Player.json` under the ignored `ops/abi/<chain-id>/` directory, or set `ETHOS_ABI_DIR` to another directory containing `<chain-id>/`. The file must contain a nonempty `abi` array and its deployed `address`. It is explicitly copied to the server. Both controller and server verify the chain and deployed bytecode; development chains 1337 and 31337 are rejected. The script does not run Hardhat or deploy contracts, and the RPC must be reachable from both machines.
5. Run `bash ops/deploy.sh` from the repository root. The script validates and privately stages Tencent Cloud certificate `bf3pwcJF` before applying server configuration. Set `ETHOS_CERTIFICATE_ID` to use another issued certificate. `bash ops/deploy.sh --help` lists the supported overrides.

### Infura RPC configuration

Use Infura for the remote Ethereum RPC by setting `ENDPOINT` in **`ops/production.env` on the deployment controller**. Do not edit `ops/deploy.sh` or put API keys in tracked files. The deployment script supports other HTTP(S) JSON-RPC providers too.

From the repository root, create the file if it does not already exist; do not overwrite an existing production configuration:

```sh
cp -n ops/production.env.example ops/production.env
chmod 600 ops/production.env
openssl rand -hex 32
```

In the Infura dashboard, select the intended network and copy its HTTPS RPC URL. For **Ethereum mainnet**, edit `ops/production.env` to contain:

```sh
ENDPOINT='https://mainnet.infura.io/v3/YOUR_INFURA_API_KEY'
ETHOS_COOKIE_SECRET='PASTE_THE_GENERATED_RANDOM_SECRET_HERE'
SLACK_SECRET=''
SLACK_CHANNEL='twinsant-com'
```

Replace both placeholders locally. Keep the API key and cookie secret private; the environment file is Git-ignored and copied to `/etc/ethos/ethos.env` on the server during deployment. Slack is optional and disabled when `SLACK_SECRET` is empty.

For **Sepolia testing**, use this endpoint instead:

```sh
ENDPOINT='https://sepolia.infura.io/v3/YOUR_INFURA_API_KEY'
```

| Network | Chain ID | Controller-side deployment files |
| --- | --- | --- |
| Ethereum mainnet | `1` | `ops/abi/1/Player.json` |
| Sepolia | `11155111` | `ops/abi/11155111/Player.json` |

Infura provides RPC access, **not contract deployment**. Local Hardhat contracts are not available on either remote network. Deploy `Player` to the chosen network first, then place its generated ABI/address file in the matching directory above. Configure the corresponding remote network in `eth/hardhat.config.js` before using Hardhat to deploy; the local setup instructions only deploy to `localhost`. Never put a wallet private key in the RPC URL.

The browser wallet must use the same network. Mainnet contract deployment and writes cost real ETH; Sepolia uses test ETH. Changing `ENDPOINT` does not migrate contracts or assets. Both the controller and server must be able to access the selected Infura endpoint; account for any Infura access restrictions and request quotas.

After configuring the endpoint, secrets, and contract files, commit and push the release code (not the ignored configuration files), then run `bash ops/deploy.sh`.

### Runtime and operations

The deployment creates an isolated Python 3.10 runtime under `/opt/ethos/.venv` from the server's Conda installation. The production Tornado process binds only to `127.0.0.1:4003`; FluffOS remains on `127.0.0.1:4001`. Nginx terminates TLS and proxies both HTTP and WebSocket traffic. Server secrets are copied to `/etc/ethos/ethos.env` with restricted permissions and are not passed on the process command line.

The target must already provide Nginx, Supervisor, Git, curl, and `/root/miniconda3/bin/conda`. Deployment requires root access through Ansible, a Linux x86-64 host for the bundled static `bin/driver.linux.x86_64`, and unused loopback ports 4001/4003 on the first deployment. The Apple Silicon driver is for local development only. The service user can write mudlib runtime data; `lib/data/` and `lib/log/` are retained between deployments. Back them up independently.

Only `ethos-driver` and `ethos-web` are updated/restarted by Supervisor. After local HTTP and driver-port checks pass, the script installs the EthOS Nginx configuration, runs `nginx -t`, and reloads Nginx. Failed TLS activation restores the previous EthOS Nginx files. A local HTTPS hostname/certificate check must pass before a missing DNS A record is created. Conflicting A/CNAME/AAAA records are not overwritten. Open TCP 80/443 in the Tencent security group; no public 4001/4003 access is needed.

This is not an atomic application rollback: an unsuccessful Python dependency install or service restart can require redeploying the previous release. The script does not touch FAPI's Conda environment or restart other Supervisor programs.

For certificate renewal, request and validate a replacement through Tencent Cloud, then rerun with `ETHOS_CERTIFICATE_ID=<new-id> bash ops/deploy.sh`. There is no automatic renewal; monitor expiration (free certificates are short-lived).

Validate the tooling locally without changing production:

```sh
bash -n ops/deploy.sh ops/run-web.sh
ansible-playbook -i ../twinsant.com/ops/ansible/inventory.ini ops/ansible/deploy.yml --syntax-check
uv run --python 3.10 python -m unittest discover -s ops/tests -v
```

## Screenshots

<img width="770" alt="image" src="https://user-images.githubusercontent.com/299586/153534242-c25e8e25-bdda-4c32-9cc2-4e21d7c4ca2e.png">


## Architecture

<img width="827" alt="image" src="https://user-images.githubusercontent.com/299586/156308820-82483660-df6a-4771-8e96-254890739bbf.png">

## Roadmap

* Phase 1: Identity + Friends + Variety + Digital Economy
* Phase 2: Anywhere + Civility + Low Friction
* Phase 3: Immersive

### 1. Identity (Blockchain NFT) 2022.1 ✅

* [SIWE/EIP-4361](https://login.xyz/)
* [Particle Auth](https://particle.network/auth-introduction.html)
* ENS
  - [https://www.fluffos.info/concepts/general/socket_efuns.html](https://www.fluffos.info/concepts/general/socket_efuns.html)
* [ENS Profile](https://medium.com/the-ethereum-name-service/step-by-step-guide-to-setting-an-nft-as-your-ens-profile-avatar-3562d39567fc)

### 2. Friends/Social (Game+education)

* Ethereum Friend List(EFL)
* Ethereum Message System(EMS)

#### Refbooks

* Human Evolution

### 3. Immersive (Interactive: NLP/AI+VR/AR/XR)

* [MagicaVoxel](http://ephtracy.github.io/)

#### Ref books

* Hooked
* **Designing with the mind in mind**
* The element of user experience
* Deep Learining

### 4. Low Friction

* 5G/6G market shares
  * 202102: China Mobile 18%, China Telecom 29.3%, China Unicom 27.6%
  * 2022
  * 2023: 33.3%
  * 2024
  * 2025: 50% Tipping Point

### 5. Variety (AIGC+UGC+PGC)

* [ai.com](https://ai.com)
* https://docs.loot.foundation/
* Wizard Role
* [LPC](https://www.fluffos.info/concepts/general/lpc.html) Editor
  - [https://www.fluffos.info/concepts/general/preprocessor.html](https://www.fluffos.info/concepts/general/preprocessor.html)
  - [LPC tutorial(Chinese documents)](https://bbs.mud.ren/threads/3)

#### Refs
* [Linden Scripting Language](http://wiki.secondlife.com/wiki/LSL_Portal)

### 6. Anywere (internet of Things)

* Discord
* iOS App
* Android App
* H5

### 7. Digital Economy (Blockchain with token)

* ERC20 Token/ERC1155
* Market Room

#### Models

* Health Point(Min-Max)
  - Magic Point
  - Intelligence quotient(IQ)
  - Emotional intelligence(EQ)
* Skill Point + Experience Point
  - Attack Point: Strength
  - Defence Point: Armor
* Work Point

#### Ref books

* **Sapiens: brief history of humankind**
* Numbers and The making of us
* Scale
* Money changes everything
* **The Origin of Wealth: Evolution, Complexity, and the Radical Remaking of Economics**
* The Great Game: The Emergence of Wall Street as a World Power
* Money mischief
* [Bitcoin: A Peer-to-Peer Electronic Cash System](https://bitcoin.org/en/bitcoin-paper)
* [工分制的制度经济学分析](https://www.cuhk.edu.hk/ics/21c/media/articles/c131-201104022.pdf)
* [A Guide to the Dungeons of Doom](https://docs.freebsd.org/44doc/usd/30.rogue/paper.pdf)

### 8. Civility (complex Network)

* DAO

#### Ref books

* [The Nature of the Firm](https://onlinelibrary.wiley.com/doi/full/10.1111/j.1468-0335.1937.tb00002.x)
* The Crowd: A Study of the Popular Mind
* Truth
* The timeless way of building
* Favor and face: Power game of chinese
* The republic of pirates
* **《中国历代政治得失》/Merits and Demerits of Political Systems in Dynastic China**


## License
See: [https://github.com/fluffos/fluffos/blob/master/Copyright](https://github.com/fluffos/fluffos/blob/master/Copyright)
LPC: https://en.wikipedia.org/wiki/LPMud
