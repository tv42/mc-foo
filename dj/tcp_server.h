#ifndef TCP_SERVER_H
#define TCP_SERVER_H

enum fd_callback_returns tcp_server_cb(struct poll_struct *ps,
                                       unsigned int fd,
                                       void **data,
                                       short *events,
                                       short revents,
                                       unsigned int flags);

#endif
