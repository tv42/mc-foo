#ifndef POLLER_H
#define POLLER_H

#include <sys/poll.h>

struct fd_handler;

enum fd_callback_returns {
  fdcb_ok,
  fdcb_remove
};

struct poll_struct;

#define POLL_STRUCT_ALLOC_BLOCK 20
struct poll_struct {
  struct pollfd *pollfds;
  struct fd_handler *fd_handlers;
  unsigned int nfds;
  unsigned int nfds_top;
};

#define POLL_FLAGS_SHUTDOWN 1

typedef enum fd_callback_returns (*fd_callback_t)(struct poll_struct *ps,
                                                  unsigned int fd,
                                                  void **data,
                                                  short *events,
                                                  short revents,
                                                  unsigned int flags);

struct fd_handler {
  fd_callback_t poll_cb;
  void *data;
};

#define init_poll_struct() {NULL, NULL, 0, 0}


int register_poll_fd(struct poll_struct *ps,
                     int fd, short events,
                     fd_callback_t poll_cb,
                     void *data);
int do_poll(struct poll_struct *ps, int timeout);

#endif
