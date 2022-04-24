inherit CORE_NPC;

void create()
{
    set("id", get_id());
    set("name", "大树");
    set("unit", "颗");

    set("hp", 200);
}

string dead()
{
    return __DIR__ "wood";
}