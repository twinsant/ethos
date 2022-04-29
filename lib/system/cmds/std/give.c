#include <ansi.h>

nosave object player;

int help(object me);

int main(object me, string arg)
{
    string name;
    string oid;
    int r;
    object e;
    object ob;
    object someone;

    player = me;

    if (!arg)
        return help(this_object());

    if (!player->reaction("give"))
    {

        write("你不能使用这个命令。\n");
        return 1;
    }

    r = sscanf(arg, "%s %s", name, oid);
    if (r==2 && oid) {
        e = environment(me);
        someone = find_player_by_name(e, name);
        if (someone)
        {
            object *i = all_inventory(me);
            if (sizeof(i) > 0) {
                if (!objectp(ob = present(oid, me))) {
                    write("你想给什么？\n");
                }
                else
                {
                    me->give(someone, ob);
                }
            } else {
                write("你一贫如洗，没什么可给的。\n");
            }
        }else{
            write(sprintf("%s不在房间里\n", name));
        }
    }else{
        return help(this_object());
    }
    return 1;
}

int help(object me)
{
    write(@HELP
命令 : give [someone] [oid]

给someone（例如0xf39）ID为oid的物品。

HELP );
    return 1;
}