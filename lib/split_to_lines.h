#ifndef SPLIT_TO_LINES_H
#define SPLIT_TO_LINES_H

#include <unistd.h>

struct split_to_lines_state {
  size_t curlen;
  size_t maxlen;
  char *curline;
  int (*line_callback)(char *, size_t, void **);
  void *line_cb_data;
};

int split_to_lines(void *buf, size_t len, void **data);

#endif
