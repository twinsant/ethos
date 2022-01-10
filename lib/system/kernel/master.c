// 调试模式开关
nosave int debug = 0;

string get_root_uid()
{

    debug_message(ctime(time()) + " : get_root_uid()!");
    return "ROOT";
}

string author_file(string str)
{
    if (debug)
    {
        debug_message("author_file : " + str);
    }

    return str;
}

string get_bb_uid()
{
    debug_message(ctime(time()) + " : get_bb_uid()!");
    return "BACKBONE";
}

string domain_file(string str)
{
    if (debug)
    {
        debug_message("domain_file : " + str);
    }

    return str;
}

object connect(int port)
{
    return new (LOGIN_OB);
}

string creator_file(string str)
{
    if (debug)
    {
        debug_message("creator_file : " + str);
    }

    return str;
}
