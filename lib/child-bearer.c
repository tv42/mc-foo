#include "child-bearer.h"
#include "poller.h"
#include "nonblock.h"

#include <unistd.h>
#include <errno.h>
#include <assert.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <stdio.h>
#include <stdlib.h>

#define BUFSIZE 1024

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
                                         int fd,
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
    /* cleanup, close pipe to child, hope it will die. */
    close(child->to_fd);
    child->to_fd=-1;
    return fdcb_ok;
  } else {
    tmp=read(fd, buf, sizeof(buf));
    if (tmp==-1 || tmp==0) {
      printf("dj: restarting child\n");
      child->pid=child->starter(child);
      if (child->pid==-1) {
	perror("dj: child won't start");
	exit(1);
      }
      close(fd);
      return fdcb_remove;
    } else {
      if (child->read_callback(buf, tmp, &child->read_cb_data)==-1) {
        close(fd);
        return fdcb_remove;
      } else {
	return fdcb_ok;
      }
    }
  }
}

#define PIPE_READ 0
#define PIPE_WRITE 1
pid_t start_by_name(struct child_bearing *child,
		    char *const args[]) {
  pid_t pid;

  unsigned int to_child[2];
  unsigned int from_child[2];

  if (pipe(to_child)==-1)
    return -1;
  if (pipe(from_child)==-1)
    return -1;

  fflush(NULL);
  pid=fork();
  if (pid==-1)
    return -1;
  if (pid>0) {                  /* parent */
    close(to_child[PIPE_READ]);
    close(from_child[PIPE_WRITE]);
    child->to_fd=to_child[PIPE_WRITE];
    if (make_nonblock(from_child[PIPE_READ]) ==-1) {
      perror("dj: make_nonblock");
      close(to_child[PIPE_WRITE]);
      close(from_child[PIPE_READ]);
      return -1;
    }
    if (register_poll_fd(child->ps,
                         from_child[PIPE_READ],
                         POLLIN,
                         read_from_child,
                         (void*)child) ==-1) {
      perror("dj: register_poll_fd");
      close(to_child[PIPE_WRITE]);
      close(from_child[PIPE_READ]);
      return -1;
    }
    return pid;
  } else {                      /* child */
    close(to_child[PIPE_WRITE]);
    close(from_child[PIPE_READ]);
    if (dup2(to_child[PIPE_READ], STDIN_FILENO) ==-1) {
      perror("dj (child): dup2");
      exit(1);
    }
    if (dup2(from_child[PIPE_WRITE], STDOUT_FILENO) ==-1) {
      perror("dj (child): dup2");
      exit(1);
    }
    close(to_child[PIPE_READ]);
    close(from_child[PIPE_WRITE]);
    execvp(args[0], args);
    fprintf(stderr, "dj (child): cannot exec %s: %s\n", 
            args[0], strerror(errno));
    exit(1);
  }
}
