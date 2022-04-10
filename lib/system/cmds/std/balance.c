#include <ansi.h>

nosave object player;

int help(object me);

int main(object me, string arg)
{
    player = me;

    WEB3_D->balance(this_object());

    return 1;
}

void on_data(mapping data)
{
    // https://docs.loot.foundation/canonical-principles/loot/loot-classification-and-ratings-system
    string msg = "";
    string k, v;

    if (data["error"]) {
        msg = sprintf(HIR "Web3 endpoint error!\n" NOR);
    } else {
        msg = sprintf("Your balance is " HIY "%.08f" NOR " ETH\n", data["balance"]);
        // debug_message(debug_info(1, player));
    }
    tell_object(player, msg);
}

int help(object me)
{
    write(@HELP
Command : balance

View player's ETH balance.

HELP );
    return 1;
}