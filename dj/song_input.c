#include "song_input.h"
#include "child-bearer.h"
#include "playqueue.h"

#include <stdlib.h>
#include <assert.h>
#include <stdio.h>

int song_input(const char *line, size_t len, void **data) {
  struct playqueue *pq;
  
  assert(data!=NULL);
  assert(*data!=NULL);
  pq=*data;

  if (add_song_media_and_backend(pq, pq->song_input->ps, 
                                 100, line, len) == -1) {
    fprintf(stderr, "dj: error in adding songs to queue.\n");
    fprintf(stderr, "dj: line was: [%.*s]\n", (int)len, line);
  } else {
    fprintf(stderr, "dj: now %d songs in queue\n", pq->songs);
  }
  return 0;
};

pid_t start_song_input(struct child_bearing *child) {
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
  state->line_callback=song_input;
  state->line_cb_data=(struct playqueue *)child->starter_data;
  child->read_callback=split_to_lines;
  child->read_cb_data=(void*)state;
  
  if ((tmp=start_by_name(child, "/usr/lib/mc-foo/lib/pick-a-song"))
      == -1) {
    free(state->curline);
    free(state);
    child->read_cb_data=NULL;
    return -1;
  }
  return tmp;
}

int init_song_input(struct poll_struct *ps, struct playqueue *pq) {
  assert(ps!=NULL);
  assert(pq!=NULL);

  pq->song_input=calloc(1, sizeof(struct child_bearing));
  if (pq->song_input==NULL)
    return -1;
  pq->song_input->ps=ps;
  pq->song_input->to_fd=-1;
  pq->song_input->pid=0;
  pq->song_input->starter=start_song_input;
  pq->song_input->starter_data=(void*)pq;
  return 0;
}
