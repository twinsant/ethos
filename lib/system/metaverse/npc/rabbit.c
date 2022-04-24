inherit CORE_NPC;

void create()
{
    set("id", get_id());
    set("name", "兔子");
    set("unit", "只");

    set("hp", 100);
}

string dead()
{
    return __DIR__ "meat";
}