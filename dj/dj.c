#include "poller.h"
#include "tcp_listener.h"
#include "song_input.h"
#include "song_output.h"
#include "playqueue.h"
#include "prof_write.h"
#include "prof_read.h"

#include <stdio.h>
#include <unistd.h>
#include <signal.h>

int main(void) {
  struct poll_struct polls=init_poll_struct();
  struct playqueue queue;
  struct write_profile wprof;
  struct read_profile rprof;

  if (signal(SIGPIPE, SIG_IGN) == SIG_ERR) {
    perror("dj: signal");
    exit(1);
  }

  if (signal(SIGCHLD, SIG_IGN) == SIG_ERR) {
    perror("dj: signal");
    exit(1);
  }

  if (init_tcp_listener(&queue, &polls) ==-1) {
    perror("dj: tcp listener initialization");
    exit(1);
  }

  playqueue_init(&queue);
  //init_write_profiles(&wprof);
  init_read_profiles(&rprof);

  if (init_song_input(&polls, &queue) ==-1) {
    perror("dj: song input initialization");
    exit(1);
  }

  if (init_song_output(&polls, &queue) ==-1) {
    perror("dj: song output initialization");
    exit(1);
  }

  while(1) {
    //printf("songs=%u, count=%d\n", queue.songs, debug_count_songs(&queue));
    request_song_input(&queue, &rprof);
    //fprintf(stderr, "request song output\n");
    request_song_output(&queue);
    //request_profile_write(&wprof);
    if (do_poll(&polls, -1)==-1) {
      perror("dj: poll");
      exit(1);
    }
  }
  shutdown_tcp();
  exit(0);
}
