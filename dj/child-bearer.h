#ifndef CHILD_BEARER_H
#define CHILD_BEARER_H

struct child_bearing {
  int from_fd;
  int to_fd;
  pid_t pid;
  pid_t (*starter)(struct child_bearing *);
  void (*read_callback)(const void *, size_t, void *);
  void *read_cb_data;
};

#endif
