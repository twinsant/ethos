#include <ansi.h>

nosave object player;

int help(object me);

int main(object me, string arg)
{
    string prefix, address;
    int amount, r;
    object e, i;
    object *ai;
    mapping transfer;

    player = me;

    if (!arg)
        return help(this_object());

    // TODO: use regex
    r = sscanf(arg, "%s %d", prefix, amount);

    if (r && prefix && strlen(prefix)>4 && amount) {
        e = environment(me);
        ai = all_inventory(e);
        foreach(i in ai) {
            if (strsrch(i->query("name"), prefix)!=-1) {
                address = i->query("address");
                tell_object(i, sprintf("\n%s is transfer %d ETH to you...\n", me->query("name"), amount));
                transfer = ([
                    "cmd":"transfer",
                    "address": address,
                    "amount":amount
                ]);
                write_cmd("Transfering...\n", "callback", transfer);
            }
        }
    } else {
        return help(this_object());
    }

    return 1;
}

int help(object me)
{
    write(@HELP
Command : give [someone] [amount]

Give someone amount ETH.

HELP );
    return 1;
}