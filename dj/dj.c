#include "poller.h"
#include "tcp_listener.h"
#include "song_input.h"
#include "playqueue.h"

#include <stdio.h>
#include <unistd.h>
#include <signal.h>

int main(void) {
  struct poll_struct polls=init_poll_struct();
  struct playqueue queue;

  if (signal(SIGPIPE, SIG_IGN) == SIG_ERR) {
    perror("dj: signal");
    exit(1);
  }

  if (signal(SIGCHLD, SIG_IGN) == SIG_ERR) {
    perror("dj: signal");
    exit(1);
  }

  if (init_tcp_listener(&polls) ==-1) {
    perror("dj: tcp listener initialization");
    exit(1);
  }

  playqueue_init(&queue);

  if (init_song_input(&polls, &queue) ==-1) {
    perror("dj: song input initialization");
    exit(1);
  }

  while(1) {
    request_song_input(&queue);
    if (do_poll(&polls, -1)==-1) {
      perror("dj: poll");
      exit(1);
    }
  }
  exit(0);
}
