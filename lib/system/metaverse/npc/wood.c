inherit CORE_NPC;

void create()
{
    set("id", get_id());

    set("name", "木头");
    set("unit", "块");
}

int reaction(string action)
{
    return 1;
}