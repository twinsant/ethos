inherit "/mudcore/cmds/player/look";

int main(object me, string arg)
{
    string s = look_all_inventory_of_room(me, me);
    if (strcmp(s, "") == 0)
    {
        write("你的背包空空如也。\n");
    }
    else
    {
        write(s);
    }
    return 1;
}