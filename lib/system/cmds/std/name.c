#include <ansi.h>

int help(object me);

int main(object me, string arg)
{
    mapping callback;

    if (arg)
    {
        callback = ([
            "cmd": "name",
            "name": arg
        ]);
        write_cmd("使用智能合约声明名字中，需要等一段时间生效...\n", "callback", callback);
    } else {
        return help(this_object());
    }
    return 1;
}

int help(object me)
{
    write(@HELP
命令 : name [your name]

设置用户名

HELP );
    return 1;
}