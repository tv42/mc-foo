#include "poller.h"

#include <assert.h>
#include <stdlib.h>
#include <errno.h>

int register_poll_fd(struct poll_struct *ps,
                     int fd, short events,
                     fd_callback_t poll_cb,
                     void *data) {
  void *alloc;
  unsigned int n;
  assert(ps!=NULL);
  assert(fd>=0);
  assert(poll_cb!=NULL);
  assert(ps->nfds>=0);
  assert(ps->nfds_top>=0);
  assert(ps->nfds<=ps->nfds_top);
  assert((ps->pollfds==NULL && ps->fd_handlers==NULL)
         || (ps->pollfds!=NULL && ps->fd_handlers!=NULL));

  if (ps->nfds==ps->nfds_top) {
    /* scan for free slots */
    n=0;
    while(n<ps->nfds && ps->pollfds[n].fd!=-1)
      n++;
    if (n>=ps->nfds) {           /* no free slot found; alloc memory */
      n=ps->nfds_top+POLL_STRUCT_ALLOC_BLOCK;
      
      alloc=realloc(ps->pollfds, n*sizeof(struct pollfd));
      if (alloc==NULL)
        return -1;
      ps->pollfds=alloc;
      
      alloc=realloc(ps->fd_handlers, n*sizeof(struct fd_handler));
      if (alloc==NULL)
        return -1;
      ps->fd_handlers=alloc;
      
      ps->nfds_top=n;
      n=ps->nfds;
      ps->nfds+=1;
    }
  } else {
    n=ps->nfds;                 /* slot after last is free and alloced */
    ps->nfds+=1;
  }

  memset(&ps->pollfds[n], 0, sizeof(struct pollfd));
  memset(&ps->fd_handlers[n], 0, sizeof(struct fd_handler));
  ps->pollfds[n].fd=fd;
  ps->pollfds[n].events=events;
  ps->fd_handlers[n].poll_cb=poll_cb;
  ps->fd_handlers[n].data=data;
  return 0;
}

int do_poll(struct poll_struct *ps, int timeout) {
  int n;
  assert(ps!=NULL);
  assert(ps->pollfds!=NULL);
  assert(ps->fd_handlers!=NULL);
  assert(ps->nfds>0);
  assert(ps->nfds_top>0);
  assert(ps->nfds<=ps->nfds_top);
  do {
    n=poll(ps->pollfds, ps->nfds, timeout);
  } while (n==-1 && errno==EINTR);
  if (n<0)
    return n;
  assert(timeout!=0 || n>=0);
  for (n=0;n<ps->nfds;n++) {
    if (ps->pollfds[n].fd==-1
        || ps->pollfds[n].revents==0)
      continue;
    assert(ps->fd_handlers[n].poll_cb!=NULL);
    switch (ps->fd_handlers[n].poll_cb(ps,
                                       ps->pollfds[n].fd,
                                       &ps->fd_handlers[n].data,
                                       &ps->pollfds[n].events,
                                       ps->pollfds[n].revents,
                                       0)) {
    case fdcb_ok:
      /* nothing */
      break;
    case fdcb_remove:
      memset(&ps->pollfds[n], 0, sizeof(struct pollfd));
      memset(&ps->fd_handlers[n], 0, sizeof(struct fd_handler));
      ps->pollfds[n].fd=-1;
      break;
    default:
      assert(1==0);
      break;
    }
  }
  return 0;
}

