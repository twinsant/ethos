string get_write_message(string msg, string cmd)
{
    mapping proto = ([
        "message": msg,
        "proxyCallback": cmd
    ]);
    string ret = json_encode(proto);
    return ret;
}

void logon()
{
    write("Hello, EthOS!\r\n");
}