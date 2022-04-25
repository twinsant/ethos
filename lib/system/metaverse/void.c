inherit CORE_STD_ROOM;

private varargs void create_json(string dest_name)
{
    string fn, json_fn, content, e, dir, dest;
    mapping j;
    string lang = this_player()->query("lang");

    if (!dest_name)
        fn = file_name();
    else
        fn = dest_name;
    if (lang && strcmp(lang, DEFAULT_LANG)) {
        json_fn = sprintf("%s-%s.json", fn, lang);
    } else {
        json_fn = fn + ".json";
    }
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
}

private varargs void create(string dest_name)
{
    debug_message(sprintf("void dest: %s", dest_name));
    create_json();
}

int denied(string verb)
{
    // allowed commands
    if (strcmp(verb, "l") == 0)
        return 0;
    if (strcmp(verb, "look") == 0)
        return 0;
    if (strcmp(verb, "g") == 0)
        return 0;
    if (strcmp(verb, "go") == 0)
        return 0;
    if (strcmp(verb, "help") == 0)
        return 0;
    if (strcmp(verb, "i") == 0)
        return 0;
    if (strcmp(verb, "inventory") == 0)
        return 0;
    return 1;
}