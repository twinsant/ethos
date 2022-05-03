### Protocol
+ 这是一个开放协议，约定了NFT进入文字元宇宙、穿梭元宇宙的基础元数据，当然，也建议了其他任何元宇宙采用本协议。
+ 简单，开放，已有工程实现Demo和相关交互设计流程。
+ 英文版请到以太坊魔法师论坛查看（building）。
+ 参考：[4955](https://ethereum-magicians.org/t/eip-4955-non-fungible-token-metadata-namespaces-extension/8746/3)
+ [Github](https://github.com/ethereum/EIPs/pull/4955)
## EIP/ERC7211
+ ERC7211协议是TextverseDAO发起，联合PlankerDAO、DAppLearningDAO的部分成员共同参与和建设的开放协议。
+ ERC7211协议是一个合成资产Token协议，为孤立的NFT进入和穿梭于不同元宇宙提供可互操作资产转化。
+ NFT具备非常大的多样性，就像许多许多产品一样散落无法统一操作，而ERC7211提供了类似于Cargo一样的封装和操作流程。
+ 协议定义了不同NFT设定的统一化互操作性的理论模型和建议实现标准。
+ 符合ERC721协议NFT经过ERC7211协议Mint合成后，生成的7211协议标准资产NFT，具备一下特性，为所有NFT插上了翅膀。
+ 协议价值

### 组成部分
+ A **public** Interoperability **Standard** for all NFTs that plan to create their own Metaverse. + It is **not** the design of your NFT Metaverse.
+ It consists of three parts: Metaverse Base Characters Protocol、NFT Transfer Protocol、Hero Transform Protocol.

+ It is an **INTERACTION** rule like a Magic Transport, make your NFT jump into any Metaverse or transform between different Metaverse.

+ The following standard allows for the implementation of a standard API for NFTs within smart contracts. 
+ This standard provides basic functionality to transfer or transform NFTs and Metaverse.

- Metaverse Base Characters Protocol
    - Metaverse name and ID.
    - Structure definition.
    - Power system definition.
    - World value and views.
    - Trading Floor support.
        - Hero Boxes.
        - Item Auto Trading Shelf.
        - Search and Compare.
- NFT Transfer Protocol
    - Hero Body description.
    - Cloth description
    - Attachment description.
    - Abilities description.
- Hero Transform Protocol
    - Upper limit characters.
    - Increasing characters range.
    - Basement link.
    - Cross world ability.
    - Can bring out of the world:
        - Characters.
        - Equipment.
        - Servants or followers.
### 0.公共用品
+ NFT资产需要具备一定的属性抽象和再定义，才可以在特定元宇宙成为映射资产，对于每个社区来说，都是巨大的工作量
+ 更何况如果各自为政，则得到的结果是资产孤岛，每次获取NFT在元宇宙间的流动性，都需要付出巨大成本，人力和时间。
+ EIP7211提供了类似于Web服务的Http协议，让你的NFT资产在得到保障的同时，获得了统一的对外互操作接口。
+ 赋予所有NFT映射元宇宙以及不同元宇宙穿行的的统一标准，丝绸一般顺滑。
### 1.开放性
+ 接受所有ERC721 NFT资产合成，ERC7211协议产品是去中心DApp，基于Ehtereum社区开放开源。
### 2.唯一性
+ 通过7211协议确保某个NFT是唯一的被Mint合成为可互操作资产NFT，通过Stake来保障唯一映射。
### 3.互操作性
+ 统一的资产管理和属性映射和能力赋能，帮助NFT快速进入和穿行于元宇宙。
### 4.合成资产
+ 提供从多样性的NFT中创造互操作性的能力赋能，即资产合成Mint。
### 5.协议DAO
+ 本协议由一个协议DAO来负责维护和升级以及日常运营，从而保障所有Mint合成的元宇宙具有可交互性。
  
## 定义元宇宙
+ 元宇宙是什么？有名字么？有唯一ID么? 在哪个链上？端口是多少？使用什么协议？客户端哪里下载？
+ 需要什么条件才可以进入？里面有多少人？主要的主题是什么？
+ 许多基础定义和描述，是进入和穿梭的基础。

## 进入元宇宙
+ 目前仅仅支持以NFT（ERC721协议为标准）来自动生成元宇宙的基础设置MetaData.
+ 对于Walker来说，购买选中的元宇宙角色NFT（很低价，游戏角色而已）即可进入选中的元宇宙。
+ 而Lord，也就是社区要创造自己的元宇宙，需要购买限量的宇宙蛋，也就是加入协议DAO（TextverseDAO subDAO），才可以创建。
+ 宇宙蛋的购买是公开的盲盒蛋，在我们第一个游戏跑起来之后，会分批创建
+ TDAO目前会根据合作关系需要，赠送4个给关系社区，例如TDAO需要宣发资源和能力，需要资金投资，则和相关DAO对接，赠送。


## 穿梭元宇宙
+ 需要遵守我们的EIP协议来生成的元宇宙的元数据，以及实现我们的Transport协议，才可以支持穿梭。
+ 所有元宇宙的收入，也来自于DAO提供的积分购买功能，Walker购买积分，则积分按照协议，80%给所有元宇宙，20%给DAO财库。
+ 所以社区越早购买宇宙蛋，生成自己的元宇宙，越早获得更多份额，份额和元宇宙蛋种类相关（3种档：标准份95%,85%,115%).
+ 标准份由DAO治理社区投票决定，投票由治理NFT投票决定，一个NFT一票，只有1024票，其中Genesis 16票，未销售前代持。
+ 因为协议+收益，决定了所有元宇宙都从技术标准和利益上支持销售的NFT来穿梭。