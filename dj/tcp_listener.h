#ifndef TCP_LISTENER_H
#define TCP_LISTENER_H

#include "poller.h"
#include "playqueue.h"

int init_tcp_listener(struct playqueue *pq, struct poll_struct *ps);

#endif
