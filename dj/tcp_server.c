#include "poller.h"
#include "child-bearer.h"
#include "song_output.h"
#include "tcp_listener.h"
#include "split_to_lines.h"

#include <unistd.h>
#include <assert.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

struct tcp_server_state {
  unsigned int fd;
  struct playqueue *pq;
};

typedef int (*tcp_action)(char *line, 
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

int tcp_server_quit(char *line, 
		    size_t len, 
		    struct tcp_server_state *state) {
  assert(state!=NULL);
  assert(state->pq!=NULL);
  shutdown_tcp();
  close(state->pq->song_input->to_fd);
  close(state->pq->song_output->to_fd);
  exit(1); //TODO close listening socket, kill children, etc..
}

int tcp_server_next(char *line, 
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

  remove_song(state->pq, state->pq->head);
  request_playing(state->pq);
  write(state->fd, "OK next song\n", 
        strlen("OK next song\n"));
  return 0;
}

int tcp_server_delete(char *line, 
                      size_t len, 
                      struct tcp_server_state *state) {
  struct queue_entry *qe;
  char ids[100];
  songid_t id;
  assert(state!=NULL);
  assert(state->pq!=NULL);

  if (len>=30) {
    write(state->fd, "ERR id too long\n", 
          strlen("ERR id too long\n"));
  } else {
    memcpy(ids, line, len);
    ids[len]='\0';
    id=stringtoid(ids);
    qe=find_id(state->pq, id);

    if (qe==state->pq->head) {
      write(state->fd, "ERR cannot remove head\n", 
            strlen("ERR cannot remove head\n"));
    } else if (qe==NULL) {
      write(state->fd, "ERR id not found\n", 
            strlen("ERR id not found\n"));
    } else {
      remove_song(state->pq, qe);
      write(state->fd, "OK removed\n", 
            strlen("OK removed\n"));
    }
  }
  return 0;
}

int tcp_server_move(char *line, 
                    size_t len, 
                    struct tcp_server_state *state) {
  struct queue_entry *qe;
  char ids[100];
  char *counts;
  signed int count;
  songid_t id;
  assert(state!=NULL);
  assert(state->pq!=NULL);

  if (len>=30) {
    write(state->fd, "ERR id too long\n", 
          strlen("ERR id too long\n"));
  } else {
    memcpy(ids, line, len);
    ids[len]='\0';
    counts=ids;
    while (counts[0]==' ')
      ++counts;
    counts=strchr(counts, ' ');
    if (counts==NULL) {
      write(state->fd, "ERR tell count too\n", 
            strlen("ERR tell count too\n"));
    } else {
      id=stringtoid(ids);
      qe=find_id(state->pq, id);
      
      if (qe==state->pq->head) {
        write(state->fd, "ERR cannot move head\n", 
              strlen("ERR cannot move head\n"));
      } else if (qe==NULL) {
        write(state->fd, "ERR id not found\n", 
              strlen("ERR id not found\n"));
      } else {
        count=strtol(counts, NULL, 0);
        if (move_song(state->pq, qe, count) < 0) {
        write(state->fd, "ERR move failed\n", 
              strlen("ERR move failed\n"));
        } else {
          write(state->fd, "OK moved\n", 
                strlen("OK moved\n"));
        }
      }
    }
  }
  return 0;
}

int tcp_server_list_queue(char *line, 
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
    tmp=snprintf(buf, 20, "%lu ", qe->id);
    if (tmp==-1 || tmp>=20) {
      perror("dj: snprintf of id");
      exit(1);
    }
    write(state->fd, buf, strlen(buf));
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

int tcp_server_status(char *line, 
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

int tcp_server_pause(char *line, 
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

int tcp_server_continue(char *line, 
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

int tcp_server_addqueue(char *line, 
			size_t len, 
			struct tcp_server_state *state) {
  size_t i;
  int priority;

  while (len && line[0]==' ') {
    line++; len--;
  }
  for (i=0; i<len; i++) {
    if (line[i]==' ')
      break;
  }
  if (i==len) {
    write(state->fd, "ERR invalid input\n", strlen("ERR invalid input\n"));
    return 0;
  }
  line[i]='\0';
  priority = strtol(line, NULL, 0);
  if (add_song_media_and_backend(state->pq,
				 state->pq->song_input->ps,
				 priority,
				 line+i+1,
				 len-i-1) == -1) {
    write(state->fd, "ERR trouble\n", strlen("ERR trouble\n"));
  } else {
    write(state->fd, "OK added\n", strlen("OK added\n"));
  }
  return 0;
}

#define TCP_SERV_OK_QUIT "OK quit\n"
#define TCP_SERV_ERR_UNIMPLEMENTED "ERR unimplemented\n"
int tcp_server_cb(char *line,
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
    { "DELETE", tcp_server_delete },
    { "MOVE", tcp_server_move },
    { "QUIT", tcp_server_quit },
    { "ADDQUEUE", tcp_server_addqueue },
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
