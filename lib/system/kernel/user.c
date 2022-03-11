inherit CORE_USER;

#include <ansi.h>

void setup()
{
    enable_living();
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
        "Hello, " HIB "%s" NOR "! Welcome to a metaverse.\n\n"
    }),
    "zh-CN": ({
        "你好， " HIB "%s" NOR "! 欢迎来到元宇宙石器时代。\n\n"
    }),
]);

function i18n_write(int ids, mixed args...)
{
    string lang = query("lang");
    write(sprintf(i18n[lang][ids], args...));
}