#include "playqueue.h"
#include <errno.h>
#include <assert.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

int find_priority(struct playqueue *queue, 
                  int n, 
                  struct priority_pointer **ppri) {
  if (ppri==NULL || queue==NULL) {
    errno=EFAULT;
    return -1;
  }
  *ppri=queue->priorities;
  while (*ppri != NULL) {
    if ((*ppri)->priority == n) {
      return 1;
    } else if ((*ppri)->priority < n) {
      *ppri=(*ppri)->next;
    } else {
      return 0;
    }    
  }
  return 0;
}

/*
 * add a new priority pointer to queue.
 * if queue->priorities is NULL, the priority list will be created.
 * Otherwise, the pointer will be inserted before pri,
 * or if pri is NULL to the tail of the priority list.
 *
 * if new is non-NULL, it *new will point to the new entry.
 *
 * use find_priority to get a value for pri; don't set it yourself.
 */
int add_priority(struct playqueue *queue,
                 struct priority_pointer *anchor,
                 int priority,
                 struct priority_pointer **new) {
  struct priority_pointer *pri;

  if (queue==NULL) {
    errno=EFAULT;
    return -1;
  }

  pri=(struct priority_pointer *)malloc(sizeof(struct priority_pointer));
  if (pri==NULL)
    return -1;
  pri->priority=priority;
  pri->insertion_point=NULL;

  if (queue->priorities==NULL) {
    pri->next=pri->prev=NULL;
    queue->priorities=queue->priority_tail=pri;
  } else if (anchor==NULL) {
    assert(queue->priority_tail!=NULL);
    pri->next=NULL;
    pri->prev=queue->priority_tail;
    queue->priority_tail->next=pri;
    queue->priority_tail=pri;
  } else {
    pri->prev=anchor->prev;
    pri->next=anchor;
    if (pri->prev)
      pri->prev->next=pri;
    anchor->prev=pri;
  }

  if (pri->prev==NULL) {
    pri->insertion_point=queue->head;
  } else {
    pri->insertion_point=pri->prev->insertion_point;
  }

  if (new!=NULL)
    *new=pri;
  return 0;
}

int find_or_add_priority(struct playqueue *queue,
                         int priority,
                         struct priority_pointer **ppri) {
  int tmp;
  struct priority_pointer *new;

  if (queue==NULL || ppri==NULL) {
    errno=EFAULT;
    return -1;
  }
  tmp=find_priority(queue, priority, ppri);
  if (tmp==-1) {
    return -1;
  } else if (tmp) {
    /* found; ppri points to it and default return is 0,
       so do nothing here */
  } else {
    /* not found */
    tmp=add_priority(queue, *ppri, priority, &new);
    if (tmp==-1)
      return -1;
    *ppri=new;
  }
  return 0;
}

int add_song(struct playqueue *queue,
             int priority,
             struct song *song) {
  struct queue_entry *qe;

  assert(song!=NULL);
  assert(song->path!=NULL);
  qe=(struct queue_entry *)malloc(sizeof(struct queue_entry));
  if (qe==NULL)
    return -1;
  qe->cache.state=not_requested;
  qe->priority=NULL;
  qe->song=*song;
  qe->song.path=malloc(strlen(song->path)+1);
  if (qe->song.path==NULL) {
    free(qe);
    return -1;
  }
  strcpy(qe->song.path, song->path); /* safe, see the malloc above */

  if (find_or_add_priority(queue, priority, &(qe->priority)) == -1) {
    free(qe->song.path);
    free(qe);
    return -1;
  }

  qe->prev=qe->priority->insertion_point;
  qe->priority->insertion_point=qe;
  if (qe->prev==NULL) {
    queue->head=qe;
  } else {
    qe->next=qe->prev->next;
  }
  if (qe->next==NULL) {
    queue->tail=qe;
  } else {
    qe->next->prev=qe;
  }
  if (qe->prev!=NULL)
    qe->prev->next=qe;
  queue->songs++;
  qe->id=new_id();
  return 0;
}

struct media *add_media(struct backend *backend,
                        char *name,
                        bitflag caching_optional,
                        bitflag caching_mandatory) {
  struct media *media;
  if (backend==NULL
      || name==NULL
      || name[0]=='\0') {
    errno=EINVAL;
    return NULL;
  }
  if ((media=(struct media*)malloc(sizeof(struct media))) ==NULL)
    return NULL;
  if ((media->name=(char*)malloc(strlen(name)+1)) ==NULL) {
    free(media);
    return NULL;
  }

  strcpy(media->name, name); /* yes, it is safe. See the malloc above */
  if (caching_optional)
    media->cache.caching_optional=1;
  if (caching_mandatory)
    media->cache.caching_mandatory=1;
  media->backend=backend;

  if (backend->medias==NULL) {
    media->next=media;
  } else {
    media->next=backend->medias;
  }
  backend->medias=media;
  return media;
}

void remove_song(struct playqueue *queue, struct queue_entry *qe) {
  struct priority_pointer *pri;

  assert(queue!=NULL);
  assert(qe!=NULL);
  assert(qe->song.path!=NULL);
  assert(queue->tail!=NULL);
  assert(qe->priority!=NULL);

  if (qe->next==NULL)
    queue->tail=qe->prev;

  if (qe->next!=NULL)
    qe->next->prev=qe->prev;
  if (qe->prev!=NULL) {
    qe->prev->next=qe->next;
    for (pri=queue->priorities; pri!=NULL; pri=pri->next) {
      if (pri->insertion_point==qe)
        pri->insertion_point=qe->prev;
    }
  } else {
    /* currently playing one, if playback is on */
    //TODO stop playing and move to next?
    
    queue->head=qe->next;
    for (pri=queue->priorities; pri!=NULL; pri=pri->next) {
      if (pri->insertion_point==qe)
        pri->insertion_point=queue->head;
    }
  }

  switch (qe->cache.state) {
  case not_requested:
    break;
  case requested:
    assert(qe->song.media->backend->cache.cancel_cache!=NULL);
    qe->song.media->backend->cache.cancel_cache(&qe->song);
    break;
  case done:
    assert(qe->song.media->backend->cache.remove_cache!=NULL);
    qe->song.media->backend->cache.remove_cache(&qe->song);
    break;
  default:
    /* something is very wrong; TODO */
    exit(42);
  }
  free(qe->song.path);
  free(qe);
  queue->songs--;
}

void remove_media(struct playqueue *queue, struct media *media) {
  struct queue_entry *cur, *next;
  struct media *m;

  assert(media->backend!=NULL);
  assert(media->backend->medias!=NULL);
  assert(media->name!=NULL);

  /*
   * remove all songs belonging to media from queue
   */
  if (queue!=NULL) {
    cur=queue->head;
    while(cur!=NULL) {
      next=cur->next;
      if (cur->song.media==media)
        remove_song(queue, cur);
      cur=next;
    }
  }

  if (media->backend->medias==media) { /* first or only media */
    if (media->next==media) {
      media->backend->medias=NULL;
    } else {
      media->backend->medias=media->next;
    }
  } else {
    m=media->backend->medias;
    
    while (m->next!=media->backend->medias) {
      if (m->next==media) {
        m->next=media->next;
        break;
      }
      m=m->next;
    }
  }

  free(media->name);
  free(media);
}

int move_song(struct playqueue *queue,
              struct queue_entry *qe,
              signed int count) {
  struct queue_entry *cur;
  struct priority_pointer *pri;

  assert(queue!=NULL);
  assert(qe!=NULL);

  /* queue->head is magical, you can't move thing above it
     (as it is there to keep record on what is playing currently */
  if (qe==queue->head)
    return -1;

  cur=qe;

  //TODO running out of queue..
  if (count<=0) {
    while (count<=0 && cur->prev!=NULL) {          /* move closer to head */
      cur=cur->prev;
      count++;
      for (pri=qe->priority; pri!=NULL; pri=pri->prev) {
        if (pri->insertion_point==cur)
          qe->priority->insertion_point=cur;
      }
    }
  } else {
    while (count>0 && cur->next!=NULL) { /* move closer to tail */
      cur=cur->next;
      count--;
      if (qe->priority->insertion_point==cur)
        qe->priority->insertion_point=qe;
      for (pri=qe->priority->next; pri!=NULL; pri=pri->next) {
        if (pri->insertion_point==cur)
          pri->insertion_point=cur;
      }
    }
  }
  assert(cur!=NULL);

  /* remove qe from old location */
  if (qe->next!=NULL) {
    qe->next->prev=qe->prev;
  } else {
    queue->tail=qe->prev;
  }
  assert(qe->prev!=NULL);
  qe->prev->next=qe->next;

  /* add below cur */
  qe->prev=cur;
  qe->next=cur->next;
  if (qe->next!=NULL) {
    qe->next->prev=qe;
  } else {
    queue->tail=qe;
  }
  qe->prev->next=qe;
  return 0;
}

int request_song_input(struct playqueue *queue, struct read_profile *prof) {
  struct read_profile *cur;
  static time_t last_time=0;

  if (queue->songs >= 20
      || (last_time!=0 && last_time > time(NULL)-2))
    return 0;

  last_time=time(NULL);

  cur=prof;
  while (cur!=NULL) {
    if (write_to_child(queue->song_input, cur->name, strlen(cur->name))==-1) {
      perror("dj: song_input");
      return -1;
    }
    cur=cur->next;
  }
  if (write_to_child(queue->song_input, "\n", strlen("\n"))==-1) {
    perror("dj: song_input");
    return -1;
  }
  return 0;
}

void playqueue_init(struct playqueue *pq) {
  assert(pq!=NULL);
  pq->head=pq->tail=NULL;
  pq->priorities=pq->priority_tail=NULL;
  pq->song_input=NULL;
  pq->song_output=NULL;
  pq->songs=0;
  pq->backends=NULL;
  pq->playing=0;
  pq->wantplaying=1;
  pq->paused=0;
}

struct backend *add_backend(struct playqueue *pq,
                            struct poll_struct *ps,
                            const char *name) {
  struct backend *be;

  be=malloc(sizeof(struct backend));
  if (be==NULL)
    return NULL;
  be->name=malloc(strlen(name)+1);
  if (be->name==NULL) {
    free(be);
    return NULL;
  }
  strcpy(be->name, name);
  be->medias=NULL;
  be->cache.request_cache=NULL;
  be->cache.cancel_cache=NULL;
  be->cache.remove_cache=NULL;
  be->cache.child.ps=ps;
  be->cache.child.to_fd=-1;
  be->cache.child.pid=0;
  be->cache.child.starter=NULL;
  be->cache.child.starter_data=NULL;
  be->cache.child.read_callback=NULL;
  be->cache.child.read_cb_data=NULL;
  //TODO caches
  if (pq->backends==NULL) {
    be->next=be;
    pq->backends=be;
  } else {
    be->next=pq->backends;
    pq->backends=be;
  }
  return be;
}

struct backend *find_backend(struct playqueue *pq, const char *name) {
  struct backend *be, *be_anchor;

  assert(pq!=NULL);
  if (pq->backends==NULL)
    return NULL;

  be_anchor=be=pq->backends;
  do {
    assert(be->name!=NULL);
    if (strcmp(be->name, name)==0)
      return be;
    be=be->next;
    assert(be!=NULL);
  } while(be_anchor!=be);
  return NULL;
}

struct media *find_media(struct backend *be, 
                         const char *name) {
  struct media *m, *m_anchor;
  assert(be!=NULL);
  if (be->medias==NULL)
    return NULL;

  m_anchor=m=be->medias;
  do {
    assert(m->name!=NULL);
    if (strcmp(m->name, name)==0)
      return m;
    m=m->next;
    assert(m!=NULL);
  } while(m_anchor!=m);
  return NULL;
}

int add_song_media_and_backend(struct playqueue *queue,
                               struct poll_struct *ps,
                               int priority,
                               const char *bms,
                               size_t len) {
  char *remember, *space;
  char *backend, *media, *song;
  struct backend *be;
  struct media *m;
  struct song s;

  space=memchr(bms, ' ', len);
  if (space==NULL || space==bms)
    return -1;
  backend=malloc(space-bms+1);
  if (backend==NULL)
    return -1;
  memcpy(backend, bms, space-bms);
  backend[space-bms]='\0';  
  be=find_backend(queue, backend);
  if (be==NULL) {
    be=add_backend(queue, ps, backend);
    if (be==NULL) {
      free(backend);
      return -1;
    }
  }
  free(backend);
  space++;
  remember=space;
  space=memchr(remember, ' ', len-(remember-bms+1));
  if (space==NULL || space==remember)
    return -1;
  media=malloc(space-remember+1);
  if (media==NULL)
    return -1;
  memcpy(media, remember, space-remember);
  media[space-remember]='\0';
  m=find_media(be, media);
  if (m==NULL) {
    m=add_media(be, media, 0, 0); //TODO bitflags
    if (m==NULL) {
      perror("dj: add_media");
      free(media);
      return -1;
    }
  }
  free(media);
  space++;
  s.media=m;
  song=malloc(len-(space-bms)+1);
  if (song==NULL)
    return -1;
  memcpy(song, space, len-(space-bms));
  song[len-(space-bms)]='\0';
  s.path=song;
  if (add_song(queue, priority, &s) ==-1) {
    free(song);
    return -1;
  }
  return 0;
}

songid_t new_id(void) {
  static songid_t last_id=0;

  return last_id++;
}

struct queue_entry *find_id(struct playqueue *pq, songid_t id) {
  struct queue_entry *qe;

  qe=pq->head;
  while (qe!=NULL && qe->id!=id) {
    qe=qe->next;
  }
  return qe;
}

songid_t stringtoid(const char *s) {
  return strtoul(s, NULL, 0); 
}

unsigned int debug_count_songs(struct playqueue *queue) {
  unsigned int n=0;
  struct queue_entry *qe=queue->head;
  while(qe!=NULL) {
    n++;
    qe=qe->next;
  }
  return n;
}
