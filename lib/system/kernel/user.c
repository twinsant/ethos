// inherit CORE_LOGIN_OB;

string write_cmd(string msg, string cmd)
{
    mapping proto = ([
        "message": msg,
        "proxyCallback": cmd
    ]);
    string ret = json_encode(proto);
    write(ret);
}

void get_did(string arg)
{
    mapping input = json_decode(arg);
    string did = input["input"];
    debug_message(did);
}

void logon()
{
    write_cmd("logon...", "DID");
    input_to("get_did");
}