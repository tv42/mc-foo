#include "playqueue.h"
#include <errno.h>
#include <assert.h>
#include <stdlib.h>

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

  qe=(struct queue_entry *)malloc(sizeof(struct queue_entry));
  if (qe==NULL)
    return -1;
  qe->cache.state=not_requested;
  qe->priority=NULL;
  qe->song=*song;

  if (find_or_add_priority(queue, priority, &(qe->priority)) == -1)
    return -1;

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
  assert(queue!=NULL);
  assert(qe!=NULL);
  assert(qe->song.path!=NULL);
  assert(queue->tail!=NULL);
  assert(qe->priority!=NULL);

  if (queue->tail==qe)
    queue->tail=qe->prev;

  qe->next->prev=qe->prev;
  if (qe->prev!=NULL) {
    qe->prev->next=qe->next;
  } else {
    /* currently playing one, if playback is on */
    //TODO stop playing and move to next?
    queue->head=qe->next;
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

void move_song(struct playqueue *queue,
              struct queue_entry *qe,
              signed int count) {
  struct queue_entry *cur;
  struct priority_pointer *pri;

  assert(queue!=NULL);
  assert(qe!=NULL);

  cur=qe;

  //TODO running out of queue..
  if (count<=0) {
    while (count<=0 && cur!=NULL) {          /* move closer to head */
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

  /* remove qe from old location */
  if (qe->next!=NULL) {
    qe->next->prev=qe->prev;
  } else {
    queue->tail=qe->prev;
  }
  if (qe->prev!=NULL) {
    qe->prev->next=qe->next;
  } else {
    queue->head=qe->next;
  }

  /* add below cur, or at the head if cur NULL */
  qe->prev=cur;
  qe->next= (cur!=NULL ? cur->next : queue->head);
  if (qe->next!=NULL) {
    qe->next->prev=qe;
  } else {
    queue->tail=qe;
  }
  if (qe->prev!=NULL) {
    qe->prev->next=qe;
  } else {
    queue->head=qe;
  }
}
