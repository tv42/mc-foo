#include "playqueue.h"
#include <stdio.h>
#include <string.h>

int main(void) {
  struct playqueue pq = {0,0,0,0};
  struct backend file = {
    NULL, "file", NULL,
    {NULL, NULL, NULL,
     {0, 0, 0, 0, 0, 0}}
  };
  struct media *m;
  struct song s;
  int tmp;

  m=add_media(&file, "cd1", 0, 0);
  if (m==NULL) {
    perror("add_media");
    exit(1);
  }    

  s.media=m;
  s.path="foobar/song1.mp3";
  tmp=add_song(&pq, 10, &s);
  if (tmp) {
    perror("add_song 1");
    exit(1);
  }

  printf("between add_songs\n");
  fflush(stdout);

  s.path="quux/song2.mp3";
  tmp=add_song(&pq, 12, &s);
  if (tmp) {
    perror("add_song 2");
    exit(1);
  }

  printf("before move_song\n");
  fflush(stdout);
  move_song(&pq, pq.tail, -1);

  printf("first song: %s\n", pq.head->song.path);
  printf("second song: %s\n", pq.head->next->song.path);
  printf("last song: %s\n", pq.tail->song.path);

  // remove_song
  // remove_media
  exit(0);
}
