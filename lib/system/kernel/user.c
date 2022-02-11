// inherit CORE_LOGIN_OB;
inherit CORE_DBASE;
inherit CORE_SAVE;

#include <ansi.h>

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
    object ob = this_object();
    mapping input = json_decode(arg);
    string did = input["input"];

    string ip_number = query_ip_number(this_object());
    if (interactive(this_object()))
        set_temp("ip_number", ip_number);

    debug_message(did + " logon at " + ip_number);

    if ((string)ob->set("id", arg) != arg)
    {
        write("Failed setting user name.\n");
        destruct(ob);
        return;
    }

    color_cat(MOTD);
    write("Hello, " HIB + did + NOR + "! Welcome to a metaverse.\n");
}

void logon()
{
    write_cmd("Getting Web3 DID...\n\n", "DID");
    input_to("get_did");
}