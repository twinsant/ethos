/**
 * The global include file is included automatically
 */

#ifndef GLOBALS_H
#define GLOBALS_H

#define DEV 1

#define LOG_DIR "/log/"

#define DATA_DIR "/data/"

#define LOGIN_OB    "/system/kernel/login"
#define USER_OB    "/system/kernel/user"
#define VOID_OB    "/system/metaverse/void"
#define WORLD_DIR   "/system/metaverse"

#define CORE_NPC "/system/metaverse/npc/object"

#define CMD_PATH_STD ({"/system/cmds/std/", "/mudcore/cmds/player/"})

#define SLACK_D "/system/daemons/slack_d"
#define CRYPTO_D "/system/daemons/crypto_d"
#define LOOT_D "/system/daemons/loot_d"
#define WEB3_D "/system/daemons/web3_d"
#define COMBAT_D "/system/daemons/combat_d"

#define DEFAULT_LANG "en-US"

#ifdef DEV
#define WIZARD "1337:0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"
#endif

#include <mudcore.h>

#ifdef MOTD
#undef MOTD
#define MOTD "/system/etc/motd"
#endif

#endif

