#ifndef PLAYQUEUE_H
#define PLAYQUEUE_H

#include <unistd.h>
#include "child-bearer.h"
#include "prof_read.h"

typedef unsigned int bitflag;
typedef unsigned long songid_t;

struct song {
  struct media *media;
  char *path;
  /* TODO */
};

struct queue_entry {
  struct queue_entry *next, *prev;
  struct priority_pointer *priority;
  songid_t id;
  struct {
    enum cache_state {
      not_requested,
      requested,
      request_failed,
      done,
    } state;
  } cache;
  struct song song;
};

struct backend {
  struct backend *next;
  const char *name;
  struct media *medias;
  struct {
    struct {
      void (*request_cache)(struct queue_entry *);
      void (*cancel_cache)(struct queue_entry *);
      void (*remove_cache)(struct queue_entry *);
    } ops;
    
    struct {
      bitflag optional: 1;
      bitflag mandatory: 1;
    } flags;
    
    struct child_bearing child; /* internal-use only */
  } cache;
};

struct media {
  struct media *next;
  char *name;
  struct backend *backend;
  struct {
    struct {
      bitflag optional: 1;
      bitflag mandatory: 1;
    } flags;
  } cache;
};

struct priority_pointer {
  struct priority_pointer *next, *prev;
  int priority;
  struct queue_entry *insertion_point;
};

struct playqueue {
  struct queue_entry *head, *tail;
  struct priority_pointer *priorities;
  struct priority_pointer *priority_tail;
  struct child_bearing *song_input;
  struct child_bearing *song_output;
  struct backend *backends;
  unsigned int songs;
  
  unsigned int playing: 1;
  unsigned int wantplaying: 1;
  unsigned int requestedplay: 1;
  unsigned int paused: 1;
};

int find_priority(struct playqueue *queue, 
                  int n, 
                  struct priority_pointer **ppri);
int add_priority(struct playqueue *queue,
                 struct priority_pointer *anchor,
                 int priority,
                 struct priority_pointer **new);
int find_or_add_priority(struct playqueue *queue,
                         int priority,
                         struct priority_pointer **ppri);
int add_song(struct playqueue *queue,
             int priority,
             struct song *song);
struct media *add_media(struct backend *backend,
                        char *name);
void remove_song(struct playqueue *queue, struct queue_entry *qe);
void remove_media(struct playqueue *queue, struct media *media);
int move_song(struct playqueue *queue,
              struct queue_entry *qe,
              signed int count);

int request_song_input(struct playqueue *queue, struct read_profile *prof);

void playqueue_init(struct playqueue *pq);

struct backend *find_backend(struct playqueue *pq, const char *name);
struct media *find_media(struct backend *be, 
                         const char *name);

int add_song_media_and_backend(struct playqueue *queue,
                               struct poll_struct *ps,
                               int priority,
                               const char *bms,
                               size_t len);

int add_backend(struct backend *be,
		struct playqueue *pq,
		struct poll_struct *ps);

songid_t new_id(void);
struct queue_entry *find_id(struct playqueue *pq, songid_t id);
songid_t stringtoid(const char *s);

unsigned int debug_count_songs(struct playqueue *queue);

#endif
