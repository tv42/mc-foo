#ifndef TCP_SERVER_H
#define TCP_SERVER_H

#include <unistd.h>

enum fd_callback_returns read_from_socket(struct poll_struct *ps,
                                          unsigned int fd,
                                          void **data,
                                          short *events,
                                          short revents,
                                          unsigned int flags);

int tcp_server_cb(const char *line,
                  size_t len,
                  void **data);

int init_tcp_server(struct poll_struct *ps, unsigned int sock);

#endif
