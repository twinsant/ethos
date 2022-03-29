#define STREAM 1
nosave mapping status = ([]);
nosave object cmd_obj;

void write_data(int fd)
{
    socket_write(fd, status[fd]["http"]);
}

void receive_data(int fd, mixed result)
{
    mapping data;

    int n = strsrch(result, "{");

    if (n > 0)
    {
        data = json_decode(trim(result[n..]));
        cmd_obj->on_data(data);
    }

    socket_close(fd);
}

void receive_callback(int fd, mixed result, string addr)
{
    debug_message(sprintf("receive %d", fd));
}

void socket_shutdown(int fd)
{
    debug_message(sprintf("shutdown %d", fd));
    socket_close(fd);
}

void balance(object cmd)
{
    int fd;
    mapping data;
    // https://github.com/Yuffster/fluffOS/blob/master/include/socket_err.h
    string body;
    string path = "/mudapi/balance";
    // mapping db;
    string cookie;
    object player;

    cmd_obj = cmd;
    status[fd] = ([]);

    fd = socket_create(STREAM, "receive_callback", "socket_shutdown");

    data = ([
    ]);
    body = json_encode(data);

    player = this_player(0);
    // debug_message(debug_info(1, player));
    // db = player->query_entire_dbase();
    // debug_message(json_encode(db));
    cookie = player->query("cookie", 1);
    status[fd]["http"] = "POST " + path + " HTTP/1.1\nHost: 127.0.0.1\nContent-Type: application/json\n" + "Cookie: " + cookie + "\nContent-Length: " + sizeof(string_encode(body, "utf-8")) + "\r\n\r\n" + body;

    socket_connect(fd, "127.0.0.1 4003", "receive_data", "write_data");
}