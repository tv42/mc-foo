#ifndef SIGCHILD_H
#define SIGCHILD_H

void sigchld_handler(int signal, siginfo_t *siginfo, void *data);
int sigchild_init(void);
int sigchild_end(void);

#endif
