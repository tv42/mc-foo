#include "poller.h"

#include <unistd.h>


enum fd_callback_returns tcp_server_cb(struct poll_struct *ps,
                                       unsigned int fd,
                                       void **data,
                                       short *events,
                                       short revents,
                                       unsigned int flags) {
  write(fd, "hi\n", 3);
  close(fd);
  return fdcb_remove;
}
