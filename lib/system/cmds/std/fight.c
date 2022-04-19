int main(object me, string arg)
{
    object ob;

    if (!arg  || !objectp(ob = present(arg, environment(me)))) {
        write("你想攻击谁？\n");
    }
    else
    {
        me->fight_ob(ob);
    }

    return 1;
}