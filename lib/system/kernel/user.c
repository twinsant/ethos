inherit CORE_LOGIN_OB;

// string write_cmd(string msg, string cmd)
// {
//     mapping proto = ([
//         "message": msg,
//         "proxyCallback": cmd
//     ]);
//     string ret = json_encode(proto);
//     write(ret);
// }

// protected void get_did(string arg)
// {
//     write_cmd("Getting Web3 DID...\r\n", "DID");
//     debug_message(("get_did " + arg));
// }

// void logon()
// {
//     input_to("get_did");
// }