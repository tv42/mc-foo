#include <stdio.h>
#include <stdarg.h>
#include <string.h>
#include <errno.h>
#include "error.h"

void errexit(const char *fmt, ...) {
  va_list args;

  fprintf(stderr, "turntable: ");
  va_start(args, fmt);
  vfprintf(stderr, fmt, args);
  va_end(args);
  fputc('\n',stderr);
  fflush(NULL);

  exit(EXIT_FAILURE);
}

void perrorexit(const char *fmt, ...) {
  va_list args;
  
  fprintf(stderr, "turntable: ");
  va_start(args, fmt);
  vfprintf(stderr, fmt, args);
  va_end(args);
  fprintf(stderr, "%s\n", strerror(errno));
  fflush(NULL);

  exit(EXIT_FAILURE);
}

void debug(const char *fmt, ...) {
  va_list args;

  fprintf(stderr, "TURNTABLE: ");
  va_start(args, fmt);
  vfprintf(stderr, fmt, args);
  va_end(args);
  fputc('\n',stderr);
  fflush(stderr);
}
