#include <ansi.h>

int help(object me);

int main(object me, string arg)
{
    debug_message("btc");

    return 1;
}

int help(object me)
{
    write(@HELP
Command : btc

Show current BTC price.

HELP );
    return 1;
}