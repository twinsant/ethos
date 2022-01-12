string get_root_uid()
{
    debug_message(ctime(time()) + " : get_root_uid()!");
    return "ROOT";
}

string author_file(string str)
{
    debug_message("author_file : " + str);
    return str;
}

string get_bb_uid()
{
    debug_message(ctime(time()) + " : get_bb_uid()!");
    return "BACKBONE";
}

object connect(int port)
{
    debug_message("connect : " + port);
    return new (__DIR__"user.c");
}

string creator_file(string str)
{
    debug_message("creator_file : " + str);
    return str;
}