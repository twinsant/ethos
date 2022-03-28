// inherit CORE_LOGIN_OB;
inherit CORE_DBASE;
inherit CORE_SAVE;

#include <ansi.h>

#define IDS_HELLO 0
#define IDS_KICK 1

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
    object user, old_logon;
    object logon = this_object();
    mapping input = json_decode(arg);
    string chain_id = input["chain_id"];
    string did = chain_id + ":" + input["input"];
    string name = input["name"];
    string cookie = input["cookie"];
    string lang = input["lang"];
    string ip_number = query_ip_number(logon);

    debug_message(sprintf("\nLogon: %O", logon));
    if (interactive(logon))
        set_temp("ip_number", ip_number);

    debug_message(did +  "(" + lang + ")" + " logon at " + ip_number);

    if ((string)logon->set("id", arg) != arg)
    {
        write("Failed setting user name.\n");
        destruct(logon);
        return;
    }

    user = find_player(did);

    if (user) {
        debug_message(sprintf("Old player found: %O", user));

        old_logon = user->query_temp("logon");
        debug_message(sprintf("Old logon: %O", old_logon));

        tell_object(user, user->i18n(IDS_KICK));
        if (interactive(user)) {
            exec(old_logon, user);
        }
        destruct(old_logon);
    }else{
        user = new(USER_OB);
        debug_message(sprintf("New player %O", user));

        user->set("lang", lang);

        user->set("id", did);
        user->set("name", name);
        user->set("cookie", cookie);
    }

    exec(user, logon);
    user->set_temp("logon", logon);

    user->i18n_color_cat(MOTD);
    user->i18n_write(IDS_HELLO, name);

    user->setup();

    debug_message("Move to " + VOID_OB);
    user->move(VOID_OB);
    tell_room(VOID_OB, "\n" + HIR + user->name() + NOR " joined.\n", ({user}));
}

void logon()
{
    write_cmd("Getting Web3 DID...\n\n", "DID");
    input_to("get_did");
}