#include <ansi.h>

nosave object player;

int help(object me);

int main(object me, string arg)
{
    string prefix, address;
    int amount, r;
    object e;
    mapping transfer;
    object someone;

    player = me;

    if (!arg)
        return help(this_object());

    // TODO: use regex
    r = sscanf(arg, "%s %d", prefix, amount);
    debug_message(sprintf("%d", r));

    if (r==2 && prefix && strlen(prefix)>4 && amount) {
        e = environment(me);
        someone = find_player(e, prefix);
        if (someone)
        {
            address = someone->query("address");
            tell_object(someone, sprintf("\n%s is transfering %d ETH to you...\n", me->query("name"), amount));
            transfer = ([
                "cmd":"transfer",
                "address": address,
                "amount":amount
            ]);
            write_cmd("Transfering...\n", "callback", transfer);
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
命令 : transfer [someone] [amount]

给someone（例如0xf39）转账amount数量的ETH.

HELP );
    return 1;
}