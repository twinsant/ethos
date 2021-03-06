inherit CORE_USER;

#include <ansi.h>

void setup()
{
    set("hp", 100);
    set("str", 100);
    set("def", 100);
    set("agi", 100);

    set_heart_beat(1);

    enable_living();
    if (query("id") == WIZARD) {
        enable_wizard();
    }
}

void heart_beat()
{
    if (is_fighting())
    {
        attack();
    }
}

int reaction(string cmd)
{
    if (strcmp(cmd, "give") == 0) {
        if (query("nameClaimed")) {
            return 1;
        } else {
            write("你还没起名字：");
        }
    }
    return 0;
}

void pick_ob(object obj)
{
    // https://www.fluffos.info/efun/interactive/commands.html ?
    if (obj->reaction("pick")) {
        // Remove ob from room
        obj->move(this_object());
        write(sprintf("你捡起了%s\n", obj->short()));
    } else {
        write(sprintf("你不能捡%s\n", obj->short()));
    }
}

void give(object someone, object ob)
{
    ob->move(someone);
    write(sprintf("你把%s给了%s\n", ob->short(), someone->name()));
    tell_object(someone, sprintf("%s把%s给了你\n", someone->name(), ob->short()));
}

function i18n_color_cat(string motd)
{
    string lang = query("lang");

    if (lang && strcmp(lang, DEFAULT_LANG)) {
        color_cat(sprintf("%s.%s", motd, lang));
    } else {
        color_cat(motd);
    }
}

mapping i18n = ([
    "en-US": ({
        "Hello, " HIB "%s" NOR "! Welcome to a metaverse.\n\n",
        "Someone kick you off.\n",
    }),
    "zh-CN": ({
        "你好， " HIB "%s" NOR "! 欢迎来到元宇宙石器时代。\n\n",
        "有人用你的账户在其他地方登录，你被迫退出\n",
    }),
]);

function i18n_write(int ids, mixed args...)
{
    string lang = query("lang");

    write(sprintf(i18n[lang][ids], args...));
}

string i18n(int ids, mixed args...)
{
    string lang = query("lang");

    return sprintf(i18n[lang][ids], args...);
}

void net_dead()
{
}