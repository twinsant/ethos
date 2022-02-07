string write_message(string msg)
{
    mapping proto = ([
        "message": msg
    ]);
    string ret = json_encode(proto);
    return ret;
}

void logon()
{
    write(write_message("Hello, EthOS!"));
}