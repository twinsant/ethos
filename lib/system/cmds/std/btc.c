#include <ansi.h>

nosave object player;

int help(object me);

int main(object me, string arg)
{
    player = me;

    CRYPTO_D->price(this_object(), "BTC");

    return 1;
}

void on_data(mapping data)
{
    string msg = sprintf("Current BTC price is " HIY "$%.2f" NOR "\r\n\r\n", data["price"]);
    // debug_message(msg);
    debug_message(debug_info(1, player));
    tell_object(player, msg);
}

int help(object me)
{
    write(@HELP
Command : btc

Show current BTC price.

HELP );
    return 1;
}