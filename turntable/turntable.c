#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/stat.h>
#include <signal.h>
#include "error.h"

typedef int (*tt_action)(const char *cmdline);

struct tt_cmd {
  const char	*cmd;
  tt_action	action;
};

/* 
 * Globals 
 */
int pid_player = 0;
int songid;

void sigchld_handler(int signal) {
  if (pid_player) {
    printf("END %i\n", songid);
    fflush(NULL);
    pid_player = 0;
  }
}

/* well, kill and wait */
int kill_player(void) {
  int ret;

  if (pid_player == 0)
    return -1;

  ret = kill(pid_player, SIGTERM);
  if (ret == 0) {
    pid_player = 0;
    waitpid(pid_player, NULL, 0);
  }
  return ret;
}

int ttplay(const char *cmdline) {
  #define SONGIDX 3
  static char *player[] = {
    "mpg123",	/* player command */
    "-b",	/* options */
    "1024",
    "",		/* song filename, pointed by SONGIDX */
    0
  };
  char *songpath;
  int id, pid;
  struct stat statbuf;

  if (pid_player) {
    /* already playing; stop old */
    if (kill_player() == -1)
      perror("turntable: kill_player");
  }
  
  /* cmdline: "PLAY id /path/to/song.mp3" */
  if (sscanf(cmdline, "PLAY %i ", &id) != 1)
    return -2;

  songpath = strstr(cmdline, "/");
  if (songpath == NULL)
    return -3;

  if (stat(songpath,&statbuf) == -1) {
    /* song does not exist */
    perror(songpath);
    printf("NOTFOUND %u %s\n", id, songpath);
    return 0;
  }

  /* debug("I'm gonna play %s", songpath); */
  player[SONGIDX] = songpath;

  signal(SIGCHLD, sigchld_handler);
  pid = fork();
  if (pid == -1) {
    perror("fork"), exit(EXIT_FAILURE);
  }
  if (pid) {
    /* parent */
    /* debug("Waiting for player to complete"); */
    pid_player = pid;
    songid = id;
    printf("PLAYING %i\n", songid);
    fflush(NULL);
  } else {
    /* child */
    /* close stdout and stderr fd's */
    close(1); close(2);
    execvp(player[0], player);
    perror("exec"), exit(EXIT_FAILURE);
  }
  return 0;
}

int ttstop(const char *cmdline) {
  int ret;
  
  if (pid_player == 0)
    return -1;

  ret = kill_player();
  if (ret == -1)
    perror("turntable: kill_player");
  if (ret == 0) {
    printf("STOP\n");
    fflush(NULL);
  }
  return ret;
}

int ttquit(const char *cmdline) {
  ttstop(NULL);
  exit(EXIT_SUCCESS);
}

int ttpause(const char *cmdline) {
  int ret;
  if (pid_player == 0)
    return -1;

  /* ignore upcoming signal due to SIGSTOP*/
  signal(SIGCHLD, SIG_IGN);

  ret = kill(pid_player, SIGSTOP);
  if (ret == -1) {
    perror("kill");
    return -2;
  }

  printf("PAUSED %i\n", songid);
  fflush(NULL);
  return 0;
}

int ttcontinue(const char *cmdline) {
  if (pid_player == 0)
    return -1;

  if (kill(pid_player, SIGCONT) == -1) {
    perror("kill");
    return -2;
  }

  /* restore handler */
  signal(SIGCHLD, sigchld_handler);

  printf("PLAYING %i\n", songid);  
  fflush(NULL);
  return 0;
}

/* wait for a command from standard input */
int readcmd() {
  static struct tt_cmd commands[] = {
    { "PLAY", ttplay },
    { "STOP", ttstop },
    { "QUIT", ttquit },
    { "PAUSE", ttpause },
    { "CONTINUE", ttcontinue },
    { 0, 0 } 
  };
  char cmd[BUFSIZ+1];
  int i, last, ret;

  if (fgets(cmd, BUFSIZ, stdin) == NULL) {
    /* EOF or some other error */
    return -1;
  }
  last = strlen(cmd)-1;
  if (last == 0)
    errexit("Error: empty command");
  if (cmd[last] != '\n')
    errexit("Too long command line %s", cmd);
  /* strip the trailing newline */
  cmd[last] = '\0';

  /* search for the command */
  for(i=0; commands[i].cmd != 0; i++) {
     if (strncmp(cmd, commands[i].cmd, strlen(commands[i].cmd)) == 0) { 
      /* command is valid */
      ret = commands[i].action(cmd);
      if (ret != 0) {
	errexit("Error executing command, got %d: %s", ret, cmd);
      }
      return 0;
    }
  }
  errexit("Invalid command: %s", cmd);
  return -1;
}


int main(int argc, char **argv) {
  while (readcmd() == 0);
  /* EOF reached; wait for the player to finish */
  if (pid_player) {
    waitpid(pid_player, NULL, 0);
  }
  return 0;
}  

