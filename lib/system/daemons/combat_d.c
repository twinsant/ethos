// 战斗守护进程
#include <ansi.h>

// https://bbs.mud.ren/threads/54
// 战斗伤害类型
#define TYPE_N 0 // 普通攻击
#define TYPE_C 1 // 会心一击

// 攻击信息
nosave string *attack_msg = ({
    "$ME无视$YOU的行动，全力发起攻击。",
    "$ME盯著$YOU的一举一动，乘$YOU没有防备突然出招。",
    "$ME慢慢地移动著脚步，然后快速攻击。",
});
// 防御攻击信息
nosave string *guard_msg = ({
    "但是$ME的攻击被$YOU格挡了。",
    "但是$YOU已有准备，不慌不忙的格挡住$ME的攻击。",
});
// 躲避攻击信息
nosave string *dodge_msg = ({
    "但是$ME的攻击被$YOU机灵地躲开了。",
    "但是$YOU左避右闪，躲过了$ME的攻击。",
    "但是$YOU已有准备，不慌不忙的躲开了$ME的攻击。",
});
// 伤害信息
string damage_msg(int damage, int type)
{
    if (damage == 0)
    {
        switch (random(3))
        {
        case 1:
            return element_of(guard_msg);
        case 2:
            return element_of(dodge_msg);
        default:
            return "但是$ME的攻击对$YOU没有造成任何伤害。";
        }
    }

    switch (type)
    {
    case TYPE_C:
        return YEL "$ME发动会心一击，对$YOU造成了 " + damage + " 点爆击伤害。";
    default:
        return "$ME对$YOU造成了 " + damage + " 点伤害。";
    }
}

void create()
{
}

// 攻击处理
void do_attack(object me, object victim)
{
/**
 * 物理伤害计算方法
 * [伤害计算值]=(攻击力/2-防御力/4)+1
 * [伤害波动]=[伤害计算值]/16+1
 * [实际伤害值]=[伤害计算值]±[伤害波动]
 */
    int attack, damage, defense, random, attack_type = TYPE_N;

    attack = me->query("str");
    defense = me->query("def");
    damage = attack / 2 - defense / 4 + 1;

/**
 * 会心伤害（暴击）无视防御
 * [会心伤害基础值]=攻击力
 */
    if (random(100) < random(me->query("agi")))
    {
        damage = attack;
        attack_type = TYPE_C;
    }
    // 伤害波动
    random = damage / 16 + 1;
    if (random(2))
    {
        damage += random;
    }
    else
    {
        damage -= random;
    }

    if (damage < 0)
    {
        damage = random(3);
    }

    msg("success", damage_msg(damage, attack_type), me, victim);

    victim->set("hp", victim->query("hp") - damage);
    if (victim->query("hp")<=0) {
        me->remove_enemy(victim);
        destruct(victim);
    }

}

// 战斗功能
void fight(object me, object victim)
{
    // 避免隔空战斗
    if (environment(me) != environment(victim))
    {
        return;
    }

    do_attack(me, victim);
}


string short()
{
    return "战斗精灵(COMBAT_D)";
}
