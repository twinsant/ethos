#define STREAM 1

nosave string host = env("HOST") || "postman-echo.com";
nosave string addr = env("ADDR") || "34.233.143.14 80";
nosave string path = env("PATH") || "/get";
nosave mapping status = ([]);

void write_data(int fd)
{
    socket_write(fd, status[fd]["http"]);
}

void receive_data(int fd, mixed result)
{
    int n = strsrch(result, "{");
    debug_message(result);


    if (n > 0)
    {
        result = json_decode(trim(result[n..]));
        debug_message(sprintf("%O", result));
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
    int ret;

    int fd = socket_create(STREAM, "receive_callback", "socket_shutdown");
    status[fd] = ([]);
    status[fd]["http"] = "GET " + path + " HTTP/1.1\nHost: " + host + "\nContent-Type: application/json;charset=UTF-8\nAuthorization: todo\r\n\r\n";

    // https://github.com/Yuffster/fluffOS/blob/master/include/socket_err.h
    ret = socket_connect(fd, addr, "receive_data", "write_data");
}