#ifndef SONG_OUTPUT_H
#define SONG_OUTPUT_H

#include "poller.h"
#include "playqueue.h"

#include <unistd.h>

int request_song_output(struct playqueue *pq);
int stop_song_output(struct playqueue *pq);
int pause_song_output(struct playqueue *pq);
int continue_song_output(struct playqueue *pq);
int request_playing(struct playqueue *pq);
int song_output(const char *line, size_t len, void **data);
pid_t start_song_output(struct child_bearing *child);
int init_song_output(struct poll_struct *ps, struct playqueue *pq);

#endif
