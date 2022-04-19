inherit CORE_STD_ROOM;

private varargs void create(int x, int y, int z)
{
    string west;
    x = 3;
    y = z = 0;

    west = __DIR__ "/" + (x - 1) + "," + y + "," + z;
    set("exits", ([
        "north" : __DIR__ "/" + x + "," + (y + 1) + "," + z,
        "south" : __DIR__ "/" + x + "," + (y - 1) + "," + z,
        "west" : west,
        "east" : __DIR__ "/" + (x + 1) + "," + y + "," + z,
    ]));

    set("short", "草地");
    set("long", "这是森林间的一大片草地，鲜花点缀其间，映衬着蓝天白云，格外美丽。");

    setArea("forest", x, y, z);
}