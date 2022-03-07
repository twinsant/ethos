/**
 * The global include file is included automatically
 */

#ifndef GLOBALS_H
#define GLOBALS_H

#define LOG_DIR "/log/"

#define DATA_DIR "/data/"

#define LOGIN_OB    "/system/kernel/login"
#define USER_OB    "/system/kernel/user"
#define VOID_OB    "/system/metaverse/void"

#define CMD_PATH_STD ({"/system/cmds/std/", "/mudcore/cmds/player/"})

#define SLACK_D "/system/daemons/slack_d"
#define CRYPTO_D "/system/daemons/crypto_d"
#define LOOT_D "/system/daemons/loot_d"

#include <mudcore.h>

#ifdef MOTD
#undef MOTD
#define MOTD "/system/etc/motd"
#endif

#endif

