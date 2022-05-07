# Engine
+ Engine is a part of the Textverse [architecture](architechure.md).
+ Engine is a series of  command chains and the background technique, like look, pick, fight, save, etc.
+ Engine can support the commands with MUDOS offchain or Smart Contract on-chain.
+ So Engine cross two parts: Docker image and Contracts.

## Commands
+ We provide text interaction between players(wizard) and the Metaverse.
+ We define the command in command_d.c for players and wizard.
+ The command list is the core ability:
+     "s":"go south",
    "n":"go north",
    "w":"go west",
    "e":"go east",
    "sd":"go southdown",
    "nd":"go northdown",
    "wd":"go westdown",
    "ed":"go eastdown",
    "su":"go southup",
    "nu":"go northup",
    "wu":"go westup",
    "eu":"go eastup",
    "sw":"go southwest",
    "se":"go southeast",
    "nw":"go northwest",
    "ne":"go northeast",
    "d":"go down",
    "u":"go up",
    "i":"inventory",
    "l":"look",
    "f":"fight",
    "p":"pick",
    "t":"transfer",
### Here are types of command: 
+ 1>View actions, E.g. pick, fight etc.
+ It was Inner Textverse the player or wizard to interaction with the object of the Metaverse.
+ Do not change anything directly.
+ It will be build from MUDOS + Hacks(almost).
+ 2>Asset actions, E.g. give, save etc.
+ It will change the Server Memory Data or off-chain Data(IPFS, Arweave..), or on-chain Data.
+ It will be build with Ethereum or Blockchain Tech and Smart Contract.

#### Save Command
+ Save can be executed manually or automated.
+ Save command will do these things:
+ 1> get the status of hero now and generate a json file.
+ 2> get the assets of inventory and generate a json file.