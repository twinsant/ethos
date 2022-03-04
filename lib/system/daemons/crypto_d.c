#define STREAM 1
nosave mapping status = ([]);

void write_data(int fd)
{
    socket_write(fd, status[fd]["http"]);
}

void receive_data(int fd, mixed result)
{
    int n = strsrch(result, "{");
    // debug_message(result);


    if (n > 0)
    {
        debug_message(sprintf("%s", result[n..]));
        result = json_decode(trim(result[n..]));
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

void price(string symbol)
{
    int fd;
    mapping data;
    // https://github.com/Yuffster/fluffOS/blob/master/include/socket_err.h
    string body;
    string path = "/mudapi/crypto";
    object player;
    // mapping db;
    string cookie;

    status[fd] = ([]);

    fd = socket_create(STREAM, "receive_callback", "socket_shutdown");

    data = ([
        "symbol": symbol
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