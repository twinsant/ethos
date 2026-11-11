#include "simul_efun/json.c"

inherit CORE_SIMUL_EFUN_OB;

string write_cmd(string msg, string callback, mixed cmd)
{
    mapping proto = ([
        "message": msg,
        callback: cmd
    ]);
    string ret = json_encode(proto);
    write(ret);
}

object load_object(string filename)
{
    debug_message((sprintf("Load object: %s", filename)));
    return efun::load_object(filename);
}

object find_player_by_prefix(object e, string prefix)
{
    object *ai;
    object match;
    string address;

    if (prefix && strlen(prefix)>4) {
        ai = all_inventory(e);
        foreach(object i in ai) {
            address = i->query("address");
            if (stringp(address) && strsrch(lower_case(address), lower_case(prefix)) == 0) {
                if (match)
                    return 0;
                match = i;
            }
        }
        return match;
    }
    return 0;
}

object find_player_by_name(object e, string name)
{
    object *ai;

    ai = all_inventory(e);
    foreach(object i in ai) {
        if (strcmp(i->query("name"), name)==0) {
            return i;
        }
    }
}
