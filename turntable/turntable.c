#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include <string.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/stat.h>
#include <signal.h>
#include <sys/poll.h>
#include <assert.h>
#include <errno.h>
#include <ctype.h>
#include "error.h"
#include "sigchild.h"

/* 
 * Globals 
 */
pid_t pid = 0;
char *songpath = NULL;
char *songid = NULL;
int paused = 0;
int stopping = 0;

void say(const char *s) {
  printf("%s\n", s);
  fflush(NULL);
}

void kill_player(void) {
  assert(pid);
  if (kill(pid, SIGTERM) == -1)
    perrorexit("killing pid %d", pid);
}

void cont_player(void) {
  assert(pid);
  if (kill(pid, SIGCONT) == -1)
    perrorexit("continuing pid %d", pid);
}

void stop_player(void) {
  assert(pid);
  if (kill(pid, SIGSTOP) == -1)
    perrorexit("stopping pid %d", pid);
}

void start_player(const char *file) {
  assert(!pid);
  pid = fork();
  if (pid == -1) {
    perror("fork");
    exit(1);
  }
  if (pid) {                    /* parent */
    fflush(NULL);
  } else {                      /* child */
    close(1);
    execlp("mpg123", "mpg123", "-q", "-b", "256", file, NULL);
    perrorexit("turntable(child): exec");
  }
}

void tt_stop(int fd) {
  if (!pid) {                   /* States START, WAIT_FOR_CONTINUE */
    if (songpath) {             /* State WAIT_FOR_CONTINUE */
      free(songpath);
      songpath=NULL;
      free(songid);
      songid=NULL;
      paused=0;
    }
    say("STOPPED");
  } else {                      /* All others */
    paused=0;
    if (songpath) {
      free(songpath);
      songpath=NULL;
      free(songid);
      songid=NULL;
    }
    if (pid)
      kill_player();
  }
}

void tt_pause(int fd) {
  if (!songpath && !paused 
      && (!pid || stopping) ) { /* States START, STOPPING */
  } else {                      /* All except START, STOPPING */
    if (!songpath && !paused && !stopping) /* State PLAYING */
      stop_player();
    paused=1;
  }
  say("PAUSED");
}

void tt_quit(int fd) {
  sigchild_end();
  if (pid)
    kill_player();
  waitpid(pid, NULL, 0);
  say("STOPPED");
  fprintf(stderr, "turntable: Shutting down.\n");
  exit(0);
}

int exists(const char *file) {
  struct stat statbuf;
  return stat(file,&statbuf)==0;
}

void tt_play(int fd) {
  char *id=NULL;
  int idlen=0;
  char *path=NULL;
  int pathlen=0;
  char *tmp;
  ssize_t n;

  /* read id, space, path, enter */
  do {
    tmp=realloc(id, ++idlen);
    if (tmp==NULL) {
      free(id);
      perrorexit("tt_play: realloc");
    }
    id=tmp;
    n=read(fd, id+idlen-1, 1);
    if (n==-1)
      perrorexit("tt_play: read from stdin");
    if (n==0)
      tt_quit(fd);
  } while(id[idlen-1]!=' ');
  id[idlen-1]='\0';
  assert(id[0]!='\0');

  do {
    tmp=realloc(path, ++pathlen);
    if (tmp==NULL) {
      free(path);
      perrorexit("tt_play: realloc");
    }
    path=tmp;
    n=read(fd, path+pathlen-1, 1);
    if (n==-1)
      perrorexit("tt_play: read from stdin");
    if (n==0)
      tt_quit(fd);
  } while(path[pathlen-1]!='\n');
  path[pathlen-1]='\0';
  assert(path[0]!='\0');

  if (!exists(path)) {          /* All states */
    printf("NOTFOUND %s\n", id);
    fflush(NULL);
    free(path);
    free(id);
    return;
  }

  free(songid);
  songid=id;
  if (songpath && pid) {        /* States WANT_NEXT, NEXT_PAUSED */
    free(songpath);
    songpath=path;
    paused=0;
  } else if (!pid) {            /* States START, WAIT_FOR_CONTINUE */
    if (songpath) {             /* State WAIT_FOR_CONTINUE */
      free(songpath);
      songpath=NULL;
      paused=0;
    }
    start_player(path);
    printf("PLAYING %s\n", id);
    fflush(NULL);
    free(path);
  } else if (stopping) {        /* State STOPPING */
    assert(!songpath);
    songpath=path;
    stopping=0;
  } else{                       /* State PAUSED, PLAYING */
    kill_player();
    if (paused) {               /* State PAUSED */
      cont_player();
      paused=0;
    }
    songpath=path;
    songid=id;
  }
}

void tt_cont(int fd) {
  if (paused && songpath && pid) { /* State NEXT_PAUSED */
    paused=0;
  } else if (paused && songpath && !pid) { /* State WAIT_FOR_CONTINUE */
    start_player(songpath);
    printf("PLAYING %s\n", songid);
    fflush(NULL);
  } else if (paused && !songpath && pid) { /* State PAUSED */
    cont_player();
  }
  say("CONTINUING");            /* All states */
}

void tt_badcommand(int fd) {
  char buf;

  do {
    switch (read(fd, &buf, 1)) {
    case -1:
      if (errno!=EAGAIN)
        perrorexit("read");
      break;
    case 0:
      tt_quit(fd);
      break;
    default:
      /* nothing */
    }
  } while(buf!='\n');
  say("BADCOMMAND");
}

enum cmd_states {
  start,
  p_ambi, pa, pau, paus, pause_,
  pl, pla, play,
  s, st, sto, stop,
  q, qu, qui, quit,
  c, co, con, cont,
  end_list
};

struct cmd_state {
  enum cmd_states s;
  char c;
  enum cmd_states new;
  void (*func)(int);
};

void readcmd(int fd) {
  const static struct cmd_state states[]= {
    {start, '\n', start, 0},
    {start, 'p', p_ambi, 0},
    {start, 's', s, 0},
    {start, 'q', q, 0},
    {start, 'c', c, 0},

    {p_ambi, 'a', pa, 0},
    {pa, 'u', pau, 0},
    {pau, 's', paus, 0},
    {paus, 'e', pause_, 0},
    {pause_, '\n', start, tt_pause},
    
    {p_ambi, 'l', pl, 0},
    {pl, 'a', pla, 0},
    {pla, 'y', play, 0},
    {play, ' ', start, tt_play},
    
    {s, 't', st, 0},
    {st, 'o', sto, 0},
    {sto, 'p', stop, 0},
    {stop, '\n', start, tt_stop},

    {q, 'u', qu, 0},
    {qu, 'i', qui, 0},
    {qui, 't', quit, 0},
    {quit, '\n', start, tt_quit},

    {c, 'o', co, 0},
    {co, 'n', con, 0},
    {con, 't', cont, 0},
    {cont, '\n', start, tt_cont},
    
    /*
     * This is a clever trick to take care of
     * both list termination and invalid states.
     * If find->s is end_list, character match
     * is not required. Thus, tt_badcommand is
     * always run when this is reached, and new
     * state is start. tt_badcommand finds the
     * next \n.
     */
    {end_list,'!',start,tt_badcommand}
  };
  static enum cmd_states state = start;
  ssize_t tmp;
  char buf;
  const struct cmd_state *find;
  
  do {
    switch (tmp=read(fd, &buf, 1)) {
    case -1:
      if (errno!=EAGAIN)
        perrorexit("read");
      break;
    case 0:
      tt_quit(fd);
      break;
    default:
      for(find=states; find->s!=end_list; find++) {
        if (find->s==state && find->c==tolower(buf))
          break;
      }
      state=find->new;
      if (find->func)
        find->func(fd);
    }
  } while (tmp>0);
}
 
void child_dead(int fd) {
  char ch;
  assert(pid);
  pid=0;
  read(fd, &ch, 1);
  if (!songpath) {
    if (stopping) {             /* State STOPPING */
      say("STOPPED");
      stopping=0;
    } else {                    /* States PLAYING, PAUSED */
      say("END");
      if (paused)               /* State PAUSED */
        paused=0;
    }
  } else if (paused) {          /* State NEXT_PAUSED */
    /* just pid=0 above */
  } else {                      /* State WANT_NEXT */
    start_player(songpath);
    free(songpath);
    songpath=NULL;
    printf("PLAYING %s\n", songid); //TODO songid is garbage the second time; DEBUG!
    fflush(NULL);
    free(songid);
    songid=NULL;
  }
}

int main(int argc, char **argv) {
  struct pollfd pollfds[2];
  int flags;

  pollfds[0].fd=0;
  pollfds[0].events=POLLIN;
  pollfds[1].fd=sigchild_init();
  pollfds[1].events=POLLIN;
  assert(pollfds[1].fd>0);
  
  /* close-on-exec */
  if (fcntl(0, F_SETFD, FD_CLOEXEC) == -1)
    perrorexit("close-on-exec on stdin");

  /* non-blocking */
  if ((flags=fcntl(0, F_GETFL)) == -1)
    perrorexit("get stdin flags");
  if (fcntl(0, F_SETFL, flags|O_NONBLOCK) == -1)
    perrorexit("set stdin flags non-block");

  for(;;) {
    switch (poll(pollfds, 2, -1)) {
    case 0:
      errexit("poll gave timeout!?!?");
    case -1:
      if (errno!=EINTR)
        perrorexit("poll");
      break;
    default:
      if (pollfds[0].revents & POLLHUP)
	tt_quit(pollfds[0].fd);
      if (pollfds[0].revents & (POLLERR|POLLNVAL))
        perrorexit("poll(stdin)");
      if (pollfds[1].revents & (POLLERR|POLLNVAL))
        perrorexit("poll(sigchld)");
      if (pollfds[1].revents&POLLIN)
        child_dead(pollfds[1].fd);
      if (pollfds[0].revents&POLLIN)
        readcmd(pollfds[0].fd);
    }
  }
}  
