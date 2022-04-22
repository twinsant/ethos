int main(object me, string arg)
{
    object ob;

    if (!arg  || !objectp(ob = present(arg, environment(me)))) {
        write("你想捡什么？\n");
    }
    else
    {
        me->pick_ob(ob);
    }

    return 1;
}