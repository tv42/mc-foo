#include "poller.h"
#include "child-bearer.h"

#include <unistd.h>
#include <assert.h>
#include <stdlib.h>
#include <stdio.h>

struct tcp_server_state {
  unsigned int fd;
};

#define BUFSIZE 1024
enum fd_callback_returns read_from_socket(struct poll_struct *ps,
                                          unsigned int fd,
                                          void **data,
                                          short *events,
                                          short revents,
                                          unsigned int flags) {
  char buf[BUFSIZE];
  ssize_t tmp;
  
  assert(ps!=NULL);
  assert(data!=NULL);
  assert(*data!=NULL);
  assert(events!=NULL);
  assert(fd>=0);

  if (flags&POLL_FLAGS_SHUTDOWN) {
    //cleanup, close socket
    close(fd);
    return fdcb_remove;
  } else {
    tmp=read(fd, buf, sizeof(buf));
    if (tmp==-1 || tmp==0) {
      close(fd);
      return fdcb_remove;
    } else {
      if (split_to_lines(buf, tmp, data) ==-1) {
        close(fd);
        return fdcb_remove;
      } else {
        return fdcb_ok;
      }      
    }
  }
}

#define TCP_SERV_ERR_UNIMPLEMENTED "ERR unimplemented\n"
#define TCP_SERV_OK_QUIT "OK quit\n"
int tcp_server_cb(const char *line,
                  size_t len,
                  void **data) {
  struct tcp_server_state *state;

  assert(data!=NULL);
  assert(*data!=NULL);
  state=*data;
  if (len==0) {
    write(state->fd, TCP_SERV_OK_QUIT, strlen(TCP_SERV_OK_QUIT));
    close(state->fd);
    return -1;
  } else {
    write(state->fd, TCP_SERV_ERR_UNIMPLEMENTED, 
          strlen(TCP_SERV_ERR_UNIMPLEMENTED));
    return 0;
  }
}

int init_tcp_server(struct poll_struct *ps, unsigned int sock) {
  struct split_to_lines_state *lines_state;
  
  lines_state=calloc(1, sizeof(struct split_to_lines_state));
  if (lines_state==NULL) {
    perror("dj: malloc");
    return -1;
  }
  lines_state->maxlen=1024;
  lines_state->curline=malloc(lines_state->maxlen);
  if (lines_state->curline==NULL) {
    perror("dj: malloc");
    free(lines_state);
    return -1;
  }
  lines_state->line_cb_data=malloc(sizeof(struct tcp_server_state));
  if (lines_state->line_cb_data==NULL) {
    perror("dj: malloc");
    free(lines_state->curline);
    free(lines_state);
    return -1;
  }
  lines_state->curlen=0;
  lines_state->line_callback=tcp_server_cb;
  ((struct tcp_server_state *)lines_state->line_cb_data)->fd=sock;
  if (register_poll_fd(ps,
                       sock, POLLIN,
                       read_from_socket, (void*)lines_state) ==-1) {
    perror("dj: register_poll_fd");
    free(lines_state->line_cb_data);
    free(lines_state->curline);
    free(lines_state);
    return -1;
  }
  return 0;
}
