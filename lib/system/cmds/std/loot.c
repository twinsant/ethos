#include <ansi.h>

nosave object player;

int help(object me);

int main(object me, string arg)
{
    player = me;

    LOOT_D->loot(this_object());

    return 1;
}

void on_data(mapping data)
{
    // https://docs.loot.foundation/canonical-principles/loot/loot-classification-and-ratings-system
    string msg = "";
    string k, v;

    foreach(k, v in data) {
        msg += sprintf("%s: %s\n", k, v);
    }
    // debug_message(msg);
    // debug_message(debug_info(1, player));
    tell_object(player, msg);
}

int help(object me)
{
    write(@HELP
Command : loot

View player's loot NFT.

HELP );
    return 1;
}