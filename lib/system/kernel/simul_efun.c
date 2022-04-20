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