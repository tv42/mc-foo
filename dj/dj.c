#include "poller.h"
#include "tcp_listener.h"
#include "song_input.h"
#include "song_output.h"
#include "playqueue.h"
#include "prof_write.h"
#include "prof_read.h"
#include "split_to_lines.h"
#include "cache.h"

#include <stdio.h>
#include <unistd.h>
#include <signal.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>

int cache_file_callback(char *line, size_t len, void **data) {
  struct playqueue *pq = *data;
  struct queue_entry *qe;

  if (len>3) {
    if (strncmp("OK ", line, 3)==0) {
      qe = find_id(pq, stringtoid(line+3));
      if (!qe) {
	printf("cacher gave ok response for invalid song id: %*s\n", len, line);
	return fdcb_ok;
      }
      if (qe->cache.state != requested) {
	printf("cacher gave ok response for not requested song id: %*s\n", len, line);
	return fdcb_ok;
      }
      qe->cache.state = done;
      return fdcb_ok;
    } else if (strncmp("ERR ", line, 4)==0) {
      qe = find_id(pq, stringtoid(line+4));
      if (!qe) {
	printf("cacher gave error response for invalid song id: %*s\n", len, line);
	return fdcb_ok;
      }
      if (qe->cache.state != requested) {
	printf("cacher gave error response for not requested song id: %*s\n", len, line);
	return fdcb_ok;
      }
      assert(qe->song.media);
      qe->cache.state = request_failed;
      if (qe->song.media->cache.flags.mandatory) {
	remove_song(pq, qe);
      }
      return fdcb_ok;
    }
  }

  printf("cacher gave invalid response: %*s\n", len, line);
  return fdcb_ok;
}

pid_t start_cache_file(struct child_bearing *child) {
  struct split_to_lines_state *state;
  pid_t tmp;
  char *const args[] = {
    "/usr/lib/mc-foo/lib/cachers/file",
    "/var/cache/mc-foo/file.tmp",
    "/var/cache/mc-foo/file",
    NULL
  };
  
  state=calloc(1, sizeof(struct split_to_lines_state));
  if (state==NULL)
    return -1;
  state->maxlen=1024;
  state->curline=malloc(state->maxlen);
  if (state->curline==NULL) {
    free(state);
    return -1;
  }
  state->curlen=0;
  state->line_callback=cache_file_callback;
  state->line_cb_data=child->starter_data;
  child->read_callback=split_to_lines;
  child->read_cb_data=(void*)state;
  
  if ((tmp=start_by_name(child, args))
      == -1) {
    free(state->curline);
    free(state);
    child->read_cb_data=NULL;
    return -1;
  }
  return tmp;
}

static void cache_file_request(struct queue_entry *qe) {
  char buf[20];
  int tmp;

  assert(qe);
  assert(qe->song.media);
  assert(qe->song.media->backend);

  tmp=snprintf(buf, 20, "%lu ", qe->id);
  if (tmp==-1 || tmp>=20) {
    perror("dj: snprintf of id");
    exit(1);
  }
  write_to_child(&qe->song.media->backend->cache.child,
		 buf, strlen(buf));
  write_to_child(&qe->song.media->backend->cache.child,
		 "/var/lib/mc-foo/media/",
		 strlen("/var/lib/mc-foo/media/"));
  write_to_child(&qe->song.media->backend->cache.child,
		 qe->song.media->backend->name,
		 strlen(qe->song.media->backend->name));
  write_to_child(&qe->song.media->backend->cache.child,
		 "/", 1);
  write_to_child(&qe->song.media->backend->cache.child,
		 qe->song.media->name,
		 strlen(qe->song.media->name));
  write_to_child(&qe->song.media->backend->cache.child,
		 "/path/", strlen("/path/"));
  write_to_child(&qe->song.media->backend->cache.child,
		 qe->song.path,
		 strlen(qe->song.path));
  write_to_child(&qe->song.media->backend->cache.child,
		 "\n", 1);
  qe->cache.state=requested;
}

void cache_file_cancel(struct queue_entry *qe) {
  char buf[20];
  int tmp;

  assert(qe);
  assert(qe->song.media);
  assert(qe->song.media->backend);
  assert(qe->cache.state==requested);

  tmp=snprintf(buf, 20, "%lu\n", qe->id);
  if (tmp==-1 || tmp>=20) {
    perror("dj: snprintf of id");
    exit(1);
  }
  write_to_child(&qe->song.media->backend->cache.child,
		 buf, strlen(buf));
  qe->cache.state=not_requested;
}

#define FILECACHEPATH "/var/cache/mc-foo/file/"
void cache_file_remove(struct queue_entry *qe) {
  char buf[20+strlen(FILECACHEPATH)];
  int tmp;

  assert(qe);
  assert(qe->song.media);
  assert(qe->song.media->backend);
  assert(qe->cache.state==done);

  tmp=snprintf(buf, 20+strlen(FILECACHEPATH), "%s%lu", FILECACHEPATH, qe->id);
  if (tmp==-1 || tmp>=20+strlen(FILECACHEPATH)) {
    perror("dj: snprintf of id");
    exit(1);
  }
  unlink(buf);
  qe->cache.state=not_requested;
}

static struct backend backend_file = {
  name: "file",
  cache: {
    ops: {
      request_cache: cache_file_request,
      cancel_cache: cache_file_cancel,
      remove_cache: cache_file_remove,
    },
    flags: {
      optional: 1,
      mandatory: 0,
    },
    child: {
      starter: start_cache_file,
      starter_data: NULL,
      read_callback: NULL,
      read_cb_data: NULL,
    },
  },
};

int main(int argc, char *argv[]) {
  struct playqueue queue;
  //TODO  struct write_profile wprof;
  struct read_profile rprof;
  struct poll_struct polls=init_poll_struct();

  if (argc>1) {
    if (!strcmp(argv[1], "help")) {
      printf("dj - play some music\n");
      exit(0);
    }
    if (!strcmp(argv[1], "usage")) {
      printf("dj\n");
      exit(0);
    }
    fprintf(stderr, "unknown argument %s\n", argv[1]);
    exit(1);
  }

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

  backend_file.cache.child.starter_data = &queue;
  if (add_backend(&backend_file, &queue, &polls) !=0) {
    perror("dj: file backend initialization");
    exit(1);
  }
  
  while(1) {
    //printf("songs=%u, count=%d\n", queue.songs, debug_count_songs(&queue));
    request_song_input(&queue, &rprof);
    //fprintf(stderr, "request song output\n");
    request_song_output(&queue);
    request_caching_queuehead(&queue, 3, 10);
    //request_profile_write(&wprof);
    if (do_poll(&polls, -1)==-1) {
      perror("dj: poll");
      exit(1);
    }
  }
  shutdown_tcp();
  exit(0);
}
