#include <stdio.h>
#include <stdarg.h>
#include "error.h"

void errexit(const char *fmt, ...) {
  va_list args;

  va_start(args, fmt);
  vfprintf(stderr, fmt, args);
  va_end(args);
  fputc('\n',stderr);

  exit(EXIT_FAILURE);
}

void debug(const char *fmt, ...) {
  va_list args;

  va_start(args, fmt);
  vfprintf(stderr, fmt, args);
  va_end(args);
  fputc('\n',stderr);
  fflush(stderr);
}
