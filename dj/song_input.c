#include "song_input.h"
#include "child-bearer.h"
#include "playqueue.h"

#include <stdlib.h>
#include <assert.h>

int song_input(const char *line, size_t len, void **data) {
  //TODO
  exit(1);
};

int init_song_input(struct poll_struct *ps, struct playqueue *pq) {
  struct split_to_lines_state *state;

  assert(ps!=NULL);
  assert(pq!=NULL);

  pq->song_input=calloc(1, sizeof(struct child_bearing));
  if (pq->song_input==NULL)
    return -1;
  state=calloc(1, sizeof(struct split_to_lines_state));
  if (state==NULL) {
    free(pq->song_input);
    return -1;
  }
  pq->song_input->ps=ps;
  pq->song_input->to_fd=-1;
  pq->song_input->pid=0;
  pq->song_input->starter=start_by_name;
  pq->song_input->starter_data=(void*)"pick-a-song";
  pq->song_input->read_callback=split_to_lines;
  state->linelen=1024;
  state->curline=NULL;
  state->line_callback=song_input;
  state->line_cb_data=NULL;
  pq->song_input->read_cb_data=(void*)state;
  return 0;
}
