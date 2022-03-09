inherit CORE_STD_ROOM;

private varargs void create(int x, int y, int z)
{
    string fn, json_fn, content, e, dir, dest;
    mapping j;

    fn = file_name();
    json_fn = fn + ".json";
    content = read_file(json_fn);
    if (content) {
        j = json_decode(content);
        set("short", j["short"]);
        set("long", j["long"]);
        set("exits", ([
        ]));
        foreach(e in j["exists"]) {
            foreach(dir, dest in e) {
                dest = replace_string(dest, "./", __DIR__);
                addExit(dir, dest);
            }
        }
    }else{
        debug_message(json_fn + " not exist!");
    }

    // SLACK_D->slack("测试 from mudlib");
}