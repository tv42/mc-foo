#ifndef CHILD_BEARER_H
#define CHILD_BEARER_H

#include <unistd.h>
#include <sys/types.h>

struct child_bearing {
  struct poll_struct *ps;
  int to_fd;
  pid_t pid;
  pid_t (*starter)(struct child_bearing *);
  void *starter_data;
  int (*read_callback)(void *, size_t, void **);
  void *read_cb_data;
};

pid_t start_by_name(struct child_bearing *child,
                    const char *prog);
enum fd_callback_returns read_from_child(struct poll_struct *ps,
                                         unsigned int fd,
                                         void **data,
                                         short *events,
                                         short revents,
                                         unsigned int flags);

ssize_t write_to_child(struct child_bearing *child, 
                       const void *buf, 
                       size_t count);

#endif