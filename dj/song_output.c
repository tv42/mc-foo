#include "song_output.h"
#include "child-bearer.h"
#include "playqueue.h"

#include <stdlib.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>

inline int min(int a, int b) {return a<=b ? a:b;}

int request_song_output(struct playqueue *pq) {
  if (pq->playing)
    return 0;                   /* already playing */
  return request_playing(pq);
}

int stop_song_output(struct playqueue *pq) {
  if (!pq->playing)
    return -1;                   /* already playing */

  write_to_child(pq->song_output, "PAUSE\n", strlen("PAUSE\n"));
  return 0;
}

int request_playing(struct playqueue *pq) {
  char buf[1024];
  int n;

  assert(pq!=NULL);
  if (pq->head==NULL)
    return -1;                   /* nothing to play yet */
  n=snprintf(buf, 1024, "PLAY %lu %s\n", pq->head->id, pq->head->song.path);
  if (n<0 || n>=1024)
    return -1;                  /* too long */
  fprintf(stderr, "dj -> turntable: %s", buf);
  write_to_child(pq->song_output, buf, n);
  return 0;
}

int song_output(const char *line, size_t len, void **data) {
  struct playqueue *pq;
  
  assert(data!=NULL);
  assert(*data!=NULL);
  pq=*data;

  if (len<3) {
    fprintf(stderr, "dj: len<3\n");
    return -1;
  }
  if (strncmp(line, "PLAYING ", strlen("PLAYING "))==0) {
    //TODO read id, remove from queue, keep in pq->playing..
    pq->paused=0;
    pq->playing=1;
  } else if (strncmp(line, "PAUSED ", strlen("PAUSED "))==0) {
    pq->paused=1;
  } else if (strncmp(line, "STOP ", strlen("STOP "))==0) {
    pq->playing=0;
  } else if (strncmp(line, "END ", strlen("END "))==0) {
    //TODO read id..
    remove_song(pq, pq->head);
    request_playing(pq);
  }
  return 0;
};

pid_t start_song_output(struct child_bearing *child) {
  struct split_to_lines_state *state;
  pid_t tmp;

  state=calloc(1, sizeof(struct split_to_lines_state));
  if (state==NULL)
    return -1;
  state->maxlen=1024;
  state->curline=malloc(state->maxlen);
  if (state->curline==NULL) {
    free(state);
    return -1;
  }
  state->curlen=0;
  state->line_callback=song_output;
  state->line_cb_data=(struct playqueue *)child->starter_data;
  child->read_callback=split_to_lines;
  child->read_cb_data=(void*)state;
  
  if ((tmp=start_by_name(child, "turntable")) ==-1) {
    free(state->curline);
    free(state);
    child->read_cb_data=NULL;
    return -1;
  }
  return tmp;
}

int init_song_output(struct poll_struct *ps, struct playqueue *pq) {
  assert(ps!=NULL);
  assert(pq!=NULL);

  pq->song_output=calloc(1, sizeof(struct child_bearing));
  if (pq->song_output==NULL)
    return -1;
  pq->song_output->ps=ps;
  pq->song_output->to_fd=-1;
  pq->song_output->pid=0;
  pq->song_output->starter=start_song_output;
  pq->song_output->starter_data=(void*)pq;
  return 0;
}
