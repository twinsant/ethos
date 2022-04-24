#include <ansi.h>

nosave object player;

int help(object me);

int main(object me, string arg)
{
    string prefix;
    string oid;
    int r;
    object e;
    object ob;
    object someone;

    player = me;

    if (!arg)
        return help(this_object());

    r = sscanf(arg, "%s %s", prefix, oid);
    if (r==2 && oid) {
        e = environment(me);
        someone = find_player(e, prefix);
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
            write(sprintf("%s不在房间里\n", prefix));
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