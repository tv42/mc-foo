#ifndef CHILD_BEARER_H
#define CHILD_BEARER_H

#include <unistd.h>
#include <sys/types.h>

struct child_bearing {
  int to_fd;
  pid_t pid;
  pid_t (*starter)(struct child_bearing *);
  int (*read_callback)(const void *, size_t, void *);
  void *read_cb_data;
};

#endif
