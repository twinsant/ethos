#include <ansi.h>

int help(object me);

int main(object me, string arg)
{
    mapping callback;

    if (arg)
    {
        callback = ([
            "cmd": "save",
            "name": arg
        ]);
        write_cmd("使用智能合约存储资产中，需要等一段时间生效...\n", "callback", callback);
    } else {
        return help(this_object());
    }
    return 1;
}

int help(object me)
{
    write(@HELP
命令 : save [your asset]

存储（更新）用户资产到链上

HELP );
    return 1;
}