void logon()
{
    mapping proto = ([
        "message": "Hello, EthOS!"
    ]);
    string ret = json_encode(proto);
    write(ret);
}