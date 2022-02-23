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

void slack(string message)
{
    int fd;
    // https://github.com/Yuffster/fluffOS/blob/master/include/socket_err.h
    string body = "";
    string path = "/mudapi/slack";

    status[fd] = ([]);

    fd = socket_create(STREAM, "receive_callback", "socket_shutdown");
    status[fd]["http"] = "POST " + path + " HTTP/1.1\nHost: 127.0.0.1\nContent-Type: application/json\nContent-Length: " + sizeof(string_encode(body, "utf-8")) + "\r\n\r\n" + body;

    socket_connect(fd, "127.0.0.1 4003", "receive_data", "write_data");
}