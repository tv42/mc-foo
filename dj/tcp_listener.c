#include "tcp_listener.h"
#include "tcp_server.h"
#include "child-bearer.h"
#include "nonblock.h"

#include <arpa/inet.h>
#include <assert.h>
#include <unistd.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <stdio.h>
#include <sys/poll.h>

#define MAX_TCP_CONNS 20

struct tcp_listener_state {
  unsigned int connections;
};

enum fd_callback_returns tcp_listener_cb(struct poll_struct *ps,
                                         unsigned int fd,
                                         void **data,
                                         short *events,
                                         short revents,
                                         unsigned int flags) {
  struct tcp_listener_state *state;
  unsigned int sock;
  struct sockaddr_in addr;
  socklen_t len;

  assert(ps!=NULL);
  assert(fd>=0);
  assert(events!=NULL);

  assert(data!=NULL);
  state=*data;
  assert(state!=NULL);

  if (ps==NULL) {
    close(fd);
    free(state);
    return fdcb_remove;
  } else {
    len=sizeof(addr);
    sock=accept(fd, &addr, &len);
    if (sock<0) {
      perror("dj: accept");
    } else {
      fprintf(stderr, "dj: incoming connection from %s port %d\n",
              inet_ntoa(addr.sin_addr),
              ntohs(addr.sin_port));
      if (make_nonblock(sock) ==-1) {
        perror("dj: make_nonblock");
        close(sock);
      }
      if (init_tcp_server(ps, sock)==-1)
        close(sock);
    }
    return fdcb_ok;
  }
}

int init_tcp(void) {
  int fd;
  struct sockaddr_in addr;

  if ((fd=socket(PF_INET, SOCK_STREAM, IPPROTO_IP)) ==-1) {
    perror("dj: socket");
    exit(1);
  }

  addr.sin_family=AF_INET;
  addr.sin_port=htons(4243);
  addr.sin_addr.s_addr=INADDR_ANY;
  if (bind(fd, &addr, sizeof(addr)) ==-1) {
    perror("dj: bind");
    exit(1);
  }
  if (listen(fd, 5) ==-1) {
    perror("dj: listen");
    exit(1);
  }
  if (make_nonblock(fd) ==-1) {
    perror("dj: make_nonblock");
    exit(1);
  }
  return fd;
}

int init_tcp_listener(struct poll_struct *ps) {
  struct tcp_listener_state *state;
  state=calloc(1, sizeof(struct tcp_listener_state));
  if (state==NULL)
    return -1;
  state->connections=0;
  if (register_poll_fd(ps, init_tcp(),
                       POLLIN,
                       tcp_listener_cb, (void*)state) <0) {
    free(state);
    return -1;
  }
  return 0;
}
