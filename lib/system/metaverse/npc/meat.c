inherit CORE_LIVING;

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

    set("name", "兔肉");
    set("unit", "块");
}