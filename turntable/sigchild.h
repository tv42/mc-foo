#ifndef SIGCHILD_H
#define SIGCHILD_H

#include <signal.h>

void sigchld_handler(int signal, siginfo_t *siginfo, void *data);
int sigchild_init(void);
int sigchild_end(void);

#endif
