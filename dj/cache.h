#ifndef CACHE_H
#define CACHE_H

#include "playqueue.h"

void request_caching_queuehead(struct playqueue *queue, int want, int max);

#endif
