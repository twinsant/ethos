#include <ansi.h>

int help(object me);

int main(object me, string arg)
{
    write("TemporalLoot is no longer available.\n");
    return 1;
}

int help(object me)
{
    write(@HELP
Command : loot

TemporalLoot is no longer available.

HELP );
    return 1;
}