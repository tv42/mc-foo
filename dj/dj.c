#include "poller.h"
#include "tcp_listener.h"

#include <stdio.h>
#include <unistd.h>

int main(void) {
  struct poll_struct polls=init_poll_struct();

  if (init_tcp_listener(&polls) ==-1) {
    perror("dj: tcp listener initialization");
    exit(1);
  }

  

  while(1) {
    if (do_poll(&polls, -1)==-1) {
      perror("dj: poll");
      exit(1);
    }
  }
  exit(0);
}
