#include "poller.h"
#include "child-bearer.h"
#include "song_output.h"
#include "tcp_listener.h"

#include <unistd.h>
#include <assert.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

struct tcp_server_state {
  unsigned int fd;
  struct playqueue *pq;
};

typedef int (*tcp_action)(const char *line, 
                          size_t len, 
                          struct tcp_server_state *state);

struct tcp_command {
  const char *cmd;
  tcp_action action;
};

#define BUFSIZE 1024
enum fd_callback_returns read_from_socket(struct poll_struct *ps,
                                          unsigned int fd,
                                          void **data,
                                          short *events,
                                          short revents,
                                          unsigned int flags) {
  char buf[BUFSIZE];
  ssize_t tmp;
  
  assert(ps!=NULL);
  assert(data!=NULL);
  assert(*data!=NULL);
  assert(events!=NULL);
  assert(fd>=0);

  if (flags&POLL_FLAGS_SHUTDOWN) { /* cleanup, close socket */
    close(fd);
    return fdcb_remove;
  } else {
    tmp=read(fd, buf, sizeof(buf));
    if (tmp==-1 || tmp==0) {
      close(fd);
      return fdcb_remove;
    } else {
      if (split_to_lines(buf, tmp, data) ==-1) {
        close(fd);
        return fdcb_remove;
      } else {
        return fdcb_ok;
      }      
    }
  }
}

int tcp_server_quit(const char *line, 
                          size_t len, 
                          struct tcp_server_state *state) {
  shutdown_tcp();
  exit(1); //TODO close listening socket, kill children, etc..
}

int tcp_server_next(const char *line, 
                          size_t len, 
                          struct tcp_server_state *state) {
  assert(state!=NULL);
  assert(state->pq!=NULL);
  //TODO check id
  if (state->pq->head==NULL 
      || !state->pq->playing 
      || !state->pq->wantplaying) {
    write(state->fd, "ERR not playing\n", 
          strlen("ERR not playing\n"));
    return 0;
  }
  if (stop_song_output(state->pq) == -1) {
    write(state->fd, "ERR cannot stop song output\n", 
          strlen("ERR cannot stop song output\n"));
    return 0;
  }

  write(state->fd, "OK next song\n", 
        strlen("OK next song\n"));
  return 0;
}

int tcp_server_list_queue(const char *line, 
                          size_t len, 
                          struct tcp_server_state *state) {
  struct queue_entry *qe;
  char buf[20];
  int tmp;

  assert(state!=NULL);
  assert(state->pq!=NULL);
  assert(state->fd>=0);
  
  write(state->fd, "MULTI queue coming...\n", 
        strlen("MULTI queue coming...\n"));
  qe=state->pq->head;
  while (qe!=NULL) {
    /* 
     * id file/_cdrom song name here.mp3
     *  foo: bar
     *  baz: quux
     */
    tmp=snprintf(buf, 20, "%lu", qe->id);
    if (tmp==-1 || tmp>=20) {
      perror("dj: snprintf of id");
      exit(1);
    }
    write(state->fd, buf, strlen(buf));
    write(state->fd, " ", 1);
    write(state->fd, 
          qe->song.media->backend->name,
          strlen(qe->song.media->backend->name));
    write(state->fd, "/", 1);
    write(state->fd, 
          qe->song.media->name,
          strlen(qe->song.media->name));
    write(state->fd, " ", 1);
    write(state->fd, qe->song.path, strlen(qe->song.path));
    write(state->fd, "\n", 1);
    write(state->fd, " foo: bar\n", strlen(" foo: bar\n"));

    qe=qe->next;
  }
  write(state->fd, ".\n", strlen(".\n"));
  return 0;
}

int tcp_server_status(const char *line, 
                     size_t len, 
                     struct tcp_server_state *state) {
  assert(state!=NULL);
  assert(state->pq!=NULL);
  write(state->fd, 
        "MULTI status coming...\n", 
        strlen("MULTI status coming...\n"));
  if (state->pq->playing) {
    write(state->fd, " playing\n", strlen(" playing\n"));
  } else {
    write(state->fd, " not playing\n", strlen(" not playing\n"));
  }
  if (state->pq->paused) {
    write(state->fd, " paused\n", strlen(" paused\n"));
  } else {
    write(state->fd, " not paused\n", strlen(" not paused\n"));
  }
  write(state->fd, ".\n", strlen(".\n"));
  return 0;
}

int tcp_server_pause(const char *line, 
                     size_t len, 
                     struct tcp_server_state *state) {
  assert(state!=NULL);
  assert(state->pq!=NULL);
  //TODO read id if there is one,
  //check with pq->head->id, complain if not equal
  if (pause_song_output(state->pq) ==-1) {
    write(state->fd, "ERR not playing\n", strlen("ERR not playing\n"));
  } else {
    write(state->fd, "OK pausing\n", strlen("OK pausing\n"));
  }
  return 0;
}

int tcp_server_continue(const char *line, 
                        size_t len, 
                        struct tcp_server_state *state) {
  assert(state!=NULL);
  assert(state->pq!=NULL);
  //TODO read id if there is one,
  //check with pq->head->id, complain if not equal
  if (continue_song_output(state->pq) ==-1) {
    write(state->fd, "ERR not playing\n", strlen("ERR not playing\n"));
  } else {
    write(state->fd, "OK continuing\n", strlen("OK continuing\n"));
  }
  return 0;
}


#define TCP_SERV_OK_QUIT "OK quit\n"
#define TCP_SERV_ERR_UNIMPLEMENTED "ERR unimplemented\n"
int tcp_server_cb(const char *line,
                  size_t len,
                  void **data) {
  int i;
  size_t size;
  size_t skip;
  struct tcp_server_state *state;
  struct tcp_command commands[] = {
    { "LIST", tcp_server_list_queue },
    { "NEXT", tcp_server_next },
    { "PAUSE", tcp_server_pause },
    { "CONTINUE", tcp_server_continue },
    { "STATUS", tcp_server_status },
    { "QUIT", tcp_server_quit },
    { 0, 0 }
  };

  assert(data!=NULL);
  assert(*data!=NULL);
  state=*data;
  if (len==0) {
    write(state->fd, TCP_SERV_OK_QUIT, strlen(TCP_SERV_OK_QUIT));
    close(state->fd);
    return -1;
  } else {
    for (i=0; commands[i].cmd != NULL; i++) {
      size=strlen(commands[i].cmd);
      skip=size;
      while (len>skip && line[skip]==' ')
        skip++;
      if ( len>=size
           && strncasecmp(line, commands[i].cmd, size)==0) {
        return commands[i].action(line+skip, len-skip, state);
      }
    }
    write(state->fd, TCP_SERV_ERR_UNIMPLEMENTED, 
          strlen(TCP_SERV_ERR_UNIMPLEMENTED));
    return 0;
  }
}

int init_tcp_server(struct playqueue *pq, 
                    struct poll_struct *ps, 
                    unsigned int sock) {
  struct split_to_lines_state *lines_state;
  
  lines_state=calloc(1, sizeof(struct split_to_lines_state));
  if (lines_state==NULL) {
    perror("dj: malloc");
    return -1;
  }
  lines_state->maxlen=1024;
  lines_state->curline=malloc(lines_state->maxlen);
  if (lines_state->curline==NULL) {
    perror("dj: malloc");
    free(lines_state);
    return -1;
  }
  lines_state->line_cb_data=malloc(sizeof(struct tcp_server_state));
  if (lines_state->line_cb_data==NULL) {
    perror("dj: malloc");
    free(lines_state->curline);
    free(lines_state);
    return -1;
  }
  lines_state->curlen=0;
  lines_state->line_callback=tcp_server_cb;
  ((struct tcp_server_state *)lines_state->line_cb_data)->fd=sock;
  ((struct tcp_server_state *)lines_state->line_cb_data)->pq=pq;
  if (register_poll_fd(ps,
                       sock, POLLIN,
                       read_from_socket, (void*)lines_state) ==-1) {
    perror("dj: register_poll_fd");
    free(lines_state->line_cb_data);
    free(lines_state->curline);
    free(lines_state);
    return -1;
  }
  return 0;
}
