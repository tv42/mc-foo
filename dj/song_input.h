#ifndef SONG_INPUT_H
#define SONG_INPUT_H

#include "poller.h"
#include "playqueue.h"

#include <unistd.h>

int song_input(const char *line, size_t len, void **data);
int init_song_input(struct poll_struct *ps, struct playqueue *pq);

#endif
