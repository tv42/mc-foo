#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <string.h>
#include <sys/errno.h>
#include <sys/sendfile.h>
#include <assert.h>

#include "nonblock.h"
#include "split_to_lines.h"
#include "poller.h"

int copies = 0;
int stdin_open = 1;

struct sending {
  char *id;
  int in;
  int out;
  off_t offset;
};

const char *dest;

/* from must be a simple file name in the current dir,
   todir must be a directory name */
int move(const char *from, const char *todir) {
  char *to;
  int ret;

  to=malloc(strlen(todir)+1+strlen(from)+1); /* todir/from\0 */
  if (!to)
    return -ENOMEM;
  strcpy(to, todir);
  strcat(to, "/");
  strcat(to, from);

  ret=rename(from, to);

  free(to);
  return ret;
}

enum fd_callback_returns read_from_file(struct poll_struct *ps,
					unsigned int fd,
					void **data,
					short *events,
					short revents,
					unsigned int flags) {
  struct sending *state;

  assert(data);
  state=*data;

  assert(state);
  assert(state->id);
  switch (sendfile(state->out, state->in, &state->offset, (size_t)-1)) {
  case -1:
    if (errno==EAGAIN || errno==EINTR)
      break;
    printf("ERR %s sendfile: %s\n", state->id, strerror(errno));
    free(state->id);
    free(state);
    copies--;
    return fdcb_remove;
  case 0:			/* EOF */
    close(state->in);
    if (close(state->out) == -1) {
      printf("ERR %s close: %s\n", state->id, strerror(errno));
    } else if (move(state->id, dest) == -1) {
      printf("ERR %s move: %s\n", state->id, strerror(errno));
    } else {      
      printf("OK %s\n", state->id);
    }
    free(state->id);
    free(state);
    copies--;
    return fdcb_remove;
    break;
  default:
    break;
  }
  return fdcb_ok;
}

static
enum fd_callback_returns remove_polling(void *id_in,
					struct fd_handler *handler) {
  const char *id=id_in;
  struct sending *snd;
  
  assert(id);
  assert(handler);

  if (handler->poll_cb != read_from_file)
    return fdcb_ok;
  
  snd=handler->data;
  assert(snd);
  assert(snd->id);
  if (strcmp(id, snd->id)==0) {
    close(snd->in);
    close(snd->out);
    unlink(snd->id);
    free(snd->id);
    free(snd);
    copies--;
    return fdcb_remove;
  }
  return fdcb_ok;
}

void abort_caching(const char *id,
		   struct poll_struct *ps) {
  poll_iterate(ps, remove_polling, (void*)id);
}

int add_command(const char *id,
		const char *file,
		struct poll_struct *ps) {
  struct sending *s;

  assert(id);
  assert(file);
  assert(ps);
  s=malloc(sizeof(struct sending));
  if (s==NULL)
    return -1;
  s->id=strdup(id);
  if (!s->id) {
    free(s);
    return -1;
  }
  assert(s->id);
  s->in=open(file, O_RDONLY|O_NONBLOCK);
  if (s->in==-1) {
    free(s->id);
    free(s);
    return -1;
  }
  s->out=open(id, O_WRONLY|O_CREAT|O_EXCL|O_NONBLOCK, S_IRUSR);
  if (s->out==-1) {
    close(s->in);
    free(s->id);
    free(s);
    return -1;
  }
  s->offset=0;
  if (register_poll_fd(ps, s->in, POLLIN,
		       read_from_file, s) == -1) {
    close(s->out);
    close(s->in);
    free(s->id);
    free(s);
    return -1;
  }
  assert(s->id);
  copies++;
  return 0;
}

int command_cb(char *line,
	       size_t len,
	       void **data) {
  size_t i;
  const char *id;

  while (len && line[0]==' ') {
    line++; len--;
  }
  for (i=0; i<len; i++) {
    if (line[i]==' ')
      break;
  }
  if (i==len) {
    line[i]='\0';
    abort_caching(line, *data);
    return 0;
  }
  line[i]='\0';
  id = line;

  line+=i+1;
  len-=i+1;

  line[len]='\0';

  if (line[0]!='/') {
    printf("ERR %s invalid input, file must have absolute path\n", id);
    return 0;
  }

  if (add_command(id, line, *data) == -1) {
    printf("ERR %s add: %s\n", id, strerror(errno));
    return 0;
  }

  return 0;
}

#define BUFSIZE 1024
enum fd_callback_returns read_stdin(struct poll_struct *ps,
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
  
  tmp=read(fd, buf, sizeof(buf));
  if (tmp==-1 || tmp==0) {
    close(fd);
    stdin_open=0;
    return fdcb_remove;
  } else {
    if (split_to_lines(buf, tmp, data) ==-1) {
      close(fd);
      stdin_open=0;
      return fdcb_remove;
    } else {
      return fdcb_ok;
    }      
  }
}

int init_command(struct poll_struct *ps) {
  struct split_to_lines_state *lines_state;

  lines_state=calloc(1, sizeof(struct split_to_lines_state));
  if (lines_state==NULL) {
    perror("cacher: malloc");
    return -1;
  }
  lines_state->maxlen=1024;
  lines_state->curline=malloc(lines_state->maxlen);
  if (lines_state->curline==NULL) {
    perror("cacher: malloc");
    free(lines_state);
    return -1;
  }
  lines_state->line_cb_data=ps;
  lines_state->curlen=0;
  lines_state->line_callback=command_cb;
  if (register_poll_fd(ps,
                       0, POLLIN,
                       read_stdin, (void*)lines_state) == -1) {
    perror("cacher: register_poll_fd");
    free(lines_state->curline);
    free(lines_state);
    return -1;
  }
  return 0;
}

int main(int argc, char *argv[]) {
  const char *temp;

  struct poll_struct ps = init_poll_struct();
  
  if (argc!=3) {
    fprintf(stderr, "cacher: usage:\n"
	    "  cacher tempdir destdir\n");
    exit(0);
  }

  temp=argv[1];
  dest=argv[2];

  assert(dest[0]=='/');

  if (chdir(temp) == -1) {
    fprintf(stderr, "cacher: change directory to %s: %s\n", 
	    temp, strerror(errno));
    exit(1);
  }

  if (make_nonblock(0) == -1) {
    perror("cacher: making stdin non-blocked");
    exit(1);
  }

  if (init_command(&ps) == -1)
    exit(1);

  while (stdin_open || copies) {
    if (do_poll(&ps, -1) == -1) {
      fprintf(stderr, "cacher: do_poll failed: %s\n", strerror(errno));
      exit(1);
    }
    fflush(NULL);		/* TODO get rid of stdio */
  }

  exit(0);
}
