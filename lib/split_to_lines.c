#include "split_to_lines.h"

#include <assert.h>
#include <stdlib.h>
#include <string.h>

#include <stdio.h>

int split_to_lines(void *buf, size_t len, void **data) {
  struct split_to_lines_state *state;
  void *line;
  void *buf_tmp;

  assert(buf!=NULL);
  assert(len>=0);
  assert(data!=NULL);
  assert(*data!=NULL);

  state=(struct split_to_lines_state*)*data;
  assert(state->curline!=NULL);
  assert(state->curlen>=0);

  buf_tmp=buf;
  while ((line=memchr(buf_tmp, '\n', 
                      len-((unsigned long)buf_tmp-(unsigned long)buf)
                      ))!=NULL) {
    if (state->curlen==0) {
      if (state->line_callback(buf_tmp, 
                               (unsigned long)line-(unsigned long)buf_tmp, 
                               &state->line_cb_data) ==-1) {
        free(state->curline);
        free(state);
        *data=NULL;
        return -1;
      }
    } else {
      /* concatenate state->curline and bytes buf_tmp..line-1 */
      if (state->curlen+(line-buf_tmp) > state->maxlen) {
        free(state->curline);
        free(state);
        *data=NULL;
        return -1;
      }
      memcpy(state->curline+state->curlen, buf_tmp, line-buf_tmp);
      state->curlen+=line-buf_tmp;
      if (state->line_callback(state->curline, 
                               state->curlen, 
                               &state->line_cb_data) ==-1) {
        free(state->curline);
        free(state);
        return -1;
      }
      state->curlen=0;
    }
    buf_tmp=line+1;
  }

  assert(buf_tmp >= buf);
  assert(buf_tmp <= buf+len);	/* I think.. */
  state->curlen = buf+len - buf_tmp;
  return 0;
}
