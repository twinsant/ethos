inherit CORE_LIVING;

int id(string arg)
{
    if (strcmp(capitalize(arg), query("id")) == 0){
        return 1;
    }
    return 0;
}

string get_id()
{
    string _id = "";
    string fn = file_name(this_object());

    int n = strsrch(fn, "/", -1);
    if (n!=-1) {
        _id = capitalize(fn[n+1..]);
    }
    return _id;
}

void create()
{
    set("id", get_id());
    set("name", "兔子");
    set("unit", "只");

    set("hp", 100);
}