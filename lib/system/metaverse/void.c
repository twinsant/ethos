inherit CORE_STD_ROOM;

private varargs void create(int x, int y, int z)
{
    set("short", "Satoshi Nakamoto Institute");
    set("long", @LONG
On January 3rd, 2009, an anonymous computer programmer (or programmers) going by the name Satoshi Nakamoto mined the first block of the Bitcoin blockchain, kickstarting the world's first fully realized crypto-currency.
LONG);

    // SLACK_D->slack("测试 from mudlib");
    set("exits", ([
        "nft": __DIR__ "loot.c",
    ]));
}