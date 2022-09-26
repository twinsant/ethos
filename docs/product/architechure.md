# Architecture Analysis

## Deploy Components
+ We have four parts to deploy.
+ 1.Dockers
+ 2.Stories
+ 3.Contracts
+ 4.Interfaces

### Docker image
+ It contains of the Core Interaction Engine and Bridge.
+ E.g. : look, fight, pick, give...
+ It will transfer from centralized to decentralized.

### Lib (Story)
+ It was the customer define and running story, mostly run by Community.
+ We will provide a KBS landing Metaverse to testify.
+ Open for DAOs.

### Protocol and Contracts
+ The EIP protocol craft is in building status: [draft 7211](https://github.com/jhfnetboy/EIPs/blob/master/EIPS/eip-7211.md).
+ And we build many contracts to provide the core ability: Transfer, Edit, Save, Load, Synthesize, Transform, Quit.
+ Also it will burn the liquidity Token to mint your new NFT of your DATA and Assets.

### Interface
+ We will build the basic interface for Web page, Mobile App and Kinect gears or voice interactions.
+ Yes, we need developers! Create funny and interesting Metaverse.
+ All the code repo is open source for Community.


```mermaid
flowchart TB
    customer1-->Interface1
    customer2-->Interface2
    customer2-->Interface3
    customer3-->InterfaceX
    customer3-->Interface2
    customerX-->InterfaceX

    subgraph all [Internet]
    Docker1-- engine -->Interface1
    Docker2-- engine -->Interface2
    Docker3-- engine -->Interface2
    Docker3-- engine -->Interface3
    DockerX-- engine -->InterfaceX
    StoryLib1-- load -->Docker1
    StoryLib1-- load -->Docker2
    StoryLib2-- load -->Docker2
    StoryLib3-- load -->Docker3
    StoryLib2-- load -->Docker3
    StoryLibX-- load -->DockerX

    Interface1-- bridge --> Transfer
    Interface2-- bridge --> Transfer
    Interface3-- bridge --> Transfer
    InterfaceX-- bridge --> Transfer

    Interface1-- bridge --> save
    Interface2-- bridge --> save
    Interface3-- bridge --> save
    InterfaceX-- bridge --> save

    Interface1-- bridge --> load
    Interface2-- bridge --> load
    Interface3-- bridge --> load
    InterfaceX-- bridge --> load    


    Interface1-- bridge --> Xcommand
    Interface2-- bridge --> Xcommand
    Interface3-- bridge --> Xcommand
    InterfaceX-- bridge --> Xcommand 

    end

    subgraph Ethereum [Ethereum]
    Transfer-- run-on --> ProtocolTextverse
    save-- run-on --> ProtocolTextverse
    load-- run-on --> ProtocolTextverse
    Xcommand-- run-on --> ProtocolTextverse
    
    Contract1 --> ProtocolTextverse
    Contract2 --> ProtocolTextverse
    Contract3 --> ProtocolTextverse
    ContractX --> ProtocolTextverse
    end
```


