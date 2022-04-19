inherit CORE_STD_ROOM;

private varargs void create(int x, int y, int z)
{
    string west;

    if (x == 1 && y == 0 && z == 0)
        west = VOID_OB;
    else
        west = __DIR__ "forest/" + (x - 1) + "," + y + "," + z;
    set("exits", ([
        "north" : __DIR__ "forest/" + x + "," + (y + 1) + "," + z,
        "south" : __DIR__ "forest/" + x + "," + (y - 1) + "," + z,
        "west" : west,
        "east" : __DIR__ "forest/" + (x + 1) + "," + y + "," + z,
    ]));

    set("short", "森林");
    set("long", "这是一片郁郁葱葱的森林，林间有不少小动物跑来跑去。");

    setArea("forest", x, y, z);

    set("objects", ([__DIR__ "npc/rabbit.c": random(3)]));
    setup();
}