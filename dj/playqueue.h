#ifndef PLAYQUEUE_H
#define PLAYQUEUE_H

#include <unistd.h>
#include "child-bearer.h"

typedef unsigned int bitflag;

struct backend {
  struct backend *next;
  char *name;
  struct media *medias;
  struct {
    void (*request_cache)(struct song *);
    struct child_bearing child; /* internal-use only */
  } cache;
}

struct media {
  struct media *next;
  char *name;
  struct backend *backend;
  struct {
    bitflag caching_optional: 1;
    bitflag caching_mandatory: 1;
  } cache;
}

struct song {
  struct media *media;
};

struct queue_entry {
  struct queue_entry *next, *prev;
  struct {
    enum cache_state {
      not_requested,
      requested,
      cancelled, /* requested but found unnecessary; when response comes,
                    remove the cached file immediately */
      done,
    } state;
  } cache;
  struct song song;
};

struct priority_pointer {
  struct priority_pointer *next, *prev;
  int priority;
  struct queue_entry *loc;
}

struct playqueue {
  struct queue_entry *head, *tail;
  struct priority_pointer *priorities;
  int count;
}

#endif
