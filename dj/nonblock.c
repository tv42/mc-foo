#include "nonblock.h"

#include <fcntl.h>
#include <unistd.h>

int make_nonblock(unsigned int fd) {
  int tmp;

  tmp=fcntl(fd, F_GETFL);
  if (tmp==-1)
    return -1;
  return fcntl(fd, F_SETFL, tmp|O_NONBLOCK);
}

