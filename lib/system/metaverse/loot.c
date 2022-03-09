
inherit CORE_STD_ROOM;

private varargs void create(int x, int y, int z)
{
    set("short", "Loot");
    set("long", @LONG
Loot is randomized adventurer gear generated and stored on chain. Stats, images, and other functionality are intentionally omitted for others to interpret. Feel free to use Loot in any way you want.
LONG);

    // SLACK_D->slack("测试 from mudlib");
    set("exits", ([
        "east": VOID_OB,
    ]));
}