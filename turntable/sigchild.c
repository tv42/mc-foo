#include <signal.h>
#include <unistd.h>
#include <fcntl.h>
#include <stdio.h>
#include "error.h"

/*
 * If we'd do the real action in the signal handler, we'd need
 * locking to prevent the handler from touching stuff from 
 * under the main code. Poll makes it simpler.
 *
 * From http://cr.yp.to/docs/selfpipe.html:
 *
 * Conventional wisdom says that you can't safely mix select() with
 * SIGCHLD (or other signals): the SIGCHLD might go off while select()
 * is starting, too early to interrupt it, too late to change its
 * timeout.
 *
 * Solution: the self-pipe trick. Maintain a pipe and select for
 * readability on the pipe input. Inside the SIGCHLD handler, write a
 * byte (non-blocking, just in case) to the pipe output. Done.
 */

int sigchild[2];

void sigchld_handler(int signal, siginfo_t *siginfo, void *data) {
  switch (siginfo->si_code) {
  case CLD_EXITED:              /* exited normally */
  case CLD_KILLED:              /* was killed */
  case SI_USER:                 /* signal sent with kill (that'd be me doing it) */
    write(sigchild[1], "\n", 1);
    break;
  default:
    fprintf(stderr, "turntable: sighandler: "
            "weird things in signal handler %d\n", siginfo->si_code);
  }
}

int sigchild_end(void) {
  struct sigaction sig;
  sig.sa_handler=SIG_IGN;
  sigemptyset(&sig.sa_mask);
  sig.sa_flags=0;
  sig.sa_sigaction=NULL;
  return sigaction(SIGCHLD, &sig, NULL);
}

int sigchild_init(void) {
  int flags;
  struct sigaction sig;

  if (pipe(sigchild) == -1)
    perrorexit("turntable: pipe");

  /* close-on-exec on */
  if (fcntl(sigchild[0], F_SETFD, FD_CLOEXEC) == -1)
    perrorexit("turntable: close-on-exec");
  if (fcntl(sigchild[1], F_SETFD, FD_CLOEXEC) == -1)
    perrorexit("turntable: close-on-exec");

  /* non-blocking */
  if ((flags=fcntl(sigchild[0], F_GETFL)) == -1)
    perrorexit("turntable: get fd flags");
  if (fcntl(sigchild[0], F_SETFL, flags|O_NONBLOCK) == -1)
    perrorexit("turntable: set fd flags non-block");
  if ((flags=fcntl(sigchild[1], F_GETFL)) == -1)
    perrorexit("turntable: get fd flags");
  if (fcntl(sigchild[1], F_SETFL, flags|O_NONBLOCK) == -1)
    perrorexit("turntable: set fd flags non-block");

  /* register signal handler */
  sig.sa_handler=NULL;
  sigemptyset(&sig.sa_mask);
  sig.sa_flags=SA_NOCLDSTOP|SA_SIGINFO; /* no signal on SIGSTOP to child */
  sig.sa_sigaction=sigchld_handler;

  if (sigaction(SIGCHLD, &sig, NULL) == -1)
    perrorexit("turntable: sigaction");

  return sigchild[0];
}
