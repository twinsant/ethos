# User journey
+ It the Product docs entrance.
+ For developers.

## Roles
+ Creator, who want to create a Metaverse of Text.
+ Player, who want to join and play the Metaverse.
+ Talker, who want to join and describe the story.
+ Wizard, who was designer of the Metaverse mechanism.

## DApp
+ The DApp named Textverse.app, it will be a Web page based text interaction game.
+ It will provide procedures to finish the different role's action.
+ Firstly will only online web page.
+ Secondly will push the mobile app to the app market.

## Main journey
### Creator
```mermaid
journey
    title Create a Metaverse of Text
    section Buy the Metaverse Egg NFT
      Go to DApp homepage: 5: Me
      Click one of Market lists: 3: Me
      Enter and buy : 2: Me, Market
    section Verify and Mint
      Go back DApp: 5: Me
      Connect Metamask and approve signature(only once): 5: Me
      Click Create my Metaverse: 3: Me, Egg
      Revoke the Metamask to verify and approve: 5: Me, Egg
      Enter Hatch the Egg page and setting: 5: Me
      Click Hatch, approve the Metamask and pay gas: 5: Me, Egg
      Finished,dashboard to manage the Metaverse: 5: Me, Metaverse

```

### Player
```mermaid
journey
    title Player how to
    section Buy the NFT with PFP(or Genesis airdrop)
      Go to DApp homepage: 5: Me
      Click one of Market lists: 3: Me
      Enter and buy : 2: Me, Market
    section Verify and Mint
      Go back DApp: 5: Me
      Connect Metamask and approve signature(only once): 5: Me
      Click Buy a Hero: 3: Me, Hero
      Revoke the Metamask to verify and approve: 5: Me, Hero
      Enter Hero page and setting: 5: Me
      Click Join, approve the Metamask and pay gas: 5: Me, Hero
      Finished,dashboard to manage the Hero, assets: 5: Me, Assets
```
### Metaverse Walker
```mermaid
journey
    title Be a Metaverse Walker
    section Be a Metaverse Player 
      Play and Earn : 5: Me
      Check Dashboard of you : 3: Me
      Level up and Mint a GT : 2: Me, GToken
    section Open and Transport
      Go to MetaverseA Transport : 5: Me, MetaverseA
      Connect Metamask and approve signature(only once): 5: Me
      Click one of Metaverse list: 3: Me, MetaverseB
      Revoke the Metamask to verify and approve: 5: Me, MetaverseB
      Enter Transport page and setting: 5: Me
      Click Transport, approve the Metamask and pay gas: 5: Me, MetaverseB
      Finished,dashboard to manage the MetaverseB: 5: Me, MetaverseB

```
### Story Talker
```mermaid
journey
    title Tell the story
    section Buy the City or Town NFT with LToken
      Go to DApp homepage: 5: Me
      Click one of NFT(Market) lists: 3: Me
      Enter and buy : 2: Me, Talker NFT
      Enter Metaverse and Buy a Town: 5: Me, Town NFT
    section Create and Earn
      Go back DApp: 5: Me
      Connect Metamask and approve signature(only once): 5: Me
      Click Create my Metaverse: 3: Me, Talker NFT
      Revoke the Metamask to verify and approve: 5: Me, Talker NFT
      Enter Dashboard and setting and Creating Story: 5: Me, Story
      Click Submit Story, be verified by the Wizard: 5: Me, Story
      Published,dashboard to manage the income: 5: Me, Town
```
### Wizard
```mermaid
journey
    title Get the Wizard NFT
    section Buy the Wizard NFT with ETH
      Go to DApp homepage: 5: Me
      Click one of NFT(Market) lists: 3: Me
      Enter and buy : 2: Me, Wizard NFT
      Enter Metaverse and Buy a Land: 5: Me, LToken NFT
    section Create and Earn
      Go back DApp: 5: Me
      Connect Metamask and approve signature(only once): 5: Me
      Click Manage my Land: 3: Me, Wizard NFT
      Revoke the Metamask to verify and approve: 5: Me, Wizard NFT
      Enter Dashboard and setting and Design Land: 5: Me, Land
      Click Audit Story, verified the Story(Invest): 5: Me, Land
      Published,dashboard to manage the income: 5: Me, Land
```

Plain Player
Long time to dev personal ability
Metaverse Walker
Depend on the Equipment and Weapons
Story Talker
Get power from the story and land after invest
Wizard
Must buy Magic books to level up, leave land down level 2
