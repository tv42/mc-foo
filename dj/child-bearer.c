#include <unistd.h>
#include "child-bearer.h"

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

void read_from_child(struct child_bearing *child, 
                        void *buf, 
                        size_t count) {
  char buf[BUFSIZE];
  ssize_t tmp;
  
  tmp=read(child->from_fd, buf, sizeof(buf));
  if (tmp==-1) {
    close(child->from_fd);
    child->from_fd=-1;
  } else if (tmp==0) {
    close(child->from_fd);
    child->from_fd=-1;
  } else {
    child->read_callback(buf, tmp, child->read_cb_data);
  }
}
