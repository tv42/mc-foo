#ifndef PLAYQUEUE_H
#define PLAYQUEUE_H

#include <unistd.h>
#include "child-bearer.h"

typedef unsigned int bitflag;

struct song {
  struct media *media;
  /* TODO */
};

struct backend {
  struct backend *next;
  char *name;
  struct media *medias;
  struct {
    void (*request_cache)(struct song *);
    void (*cancel_cache)(struct song *);
    void (*remove_cache)(struct song *);
    struct child_bearing child; /* internal-use only */
  } cache;
};

struct media {
  struct media *next;
  char *name;
  struct backend *backend;
  struct {
    bitflag caching_optional: 1;
    bitflag caching_mandatory: 1;
  } cache;
};

struct queue_entry {
  struct queue_entry *next, *prev;
  struct {
    enum cache_state {
      not_requested,
      requested,
      done,
    } state;
  } cache;
  struct song song;
};

struct priority_pointer {
  struct priority_pointer *next, *prev;
  int priority;
  struct queue_entry *loc;
};

struct playqueue {
  struct queue_entry *head, *tail;
  struct priority_pointer *priorities;
  struct priority_pointer *priority_tail;
  int count;
};

#endif
