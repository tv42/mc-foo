#ifndef ERROR_H
#define ERROR_H

#include <stdlib.h>

void errexit(const char *fmt, ...);
void debug(const char *fmt, ...);
void perrorexit(const char *fmt, ...);

#endif
