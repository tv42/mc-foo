#include "child-bearer.h"
#include "poller.h"

#include <unistd.h>
#include <errno.h>
#include <assert.h>

#define BUFSIZE 1024

//remember to install the signal handler to ignore SIGPIPE
ssize_t write_to_child(struct child_bearing *child, 
                       const void *buf, 
                       size_t count) {
  ssize_t tmp;
  if (child->pid<=0) {
    child->pid=child->starter(child);
    if (child->pid==-1)
      return -1;
  }
  do {
    tmp=write(child->to_fd, buf, count);
    if (tmp==-1) {
      switch (errno) {
      case EBADF:
      case EPIPE:
        child->pid=child->starter(child);
        if (child->pid==-1)
          return -1;
        break;
      case EINTR:
        break;
      default:
        return -1;
      }
    }
  } while(tmp==-1);
  return tmp;
}

enum fd_callback_returns read_from_child(struct poll_struct *ps,
                                         unsigned int fd,
                                         void **data,
                                         short *events,
                                         short revents,
                                         unsigned int flags) {
  struct child_bearing *child;
  char buf[BUFSIZE];
  ssize_t tmp;

  assert(ps!=NULL);
  assert(data!=NULL);
  assert(*data!=NULL);
  assert(events!=NULL);
  assert(fd>=0);

  child=(struct child_bearing*) *data;
  if (flags&POLL_FLAGS_SHUTDOWN) {
    //cleanup, close pipe to child, hope it will die.
    close(child->to_fd);
    child->to_fd=-1;
    return fdcb_ok;
  } else {
    tmp=read(fd, buf, sizeof(buf));
    if (tmp==-1 || tmp==0) {
      close(fd);
      return fdcb_remove;
    } else {
      if (child->read_callback(buf, tmp, child->read_cb_data)) {
        return fdcb_ok;
      } else {
        close(fd);
        return fdcb_remove;
      }      
    }
  }
}
