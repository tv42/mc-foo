#ifndef PROFILE_WRITE_H
#define PROFILE_WRITE_H

#include "child-bearer.h"

struct score {
  struct score *next;
  char *type;
  char *name;
  signed int adjust;
};

struct write_profile {
  struct profile *next;
  char *name;
  struct score *scores;
  struct child_bearing child;	/* internal use only */
};

void init_write_profiles(struct write_profile *head);
struct write_profile *add_write_profile(struct write_profile *head, 
					const char *name);
struct write_profile *find_write_profile(struct write_profile *head, 
					 const char *name);
struct score *add_score(struct write_profile *prof,
			const char *type,
			const char *name,
			signed int adjust);
struct score *find_and_add_score(struct write_profile *head,
				 const char *prof,
				 const char *type,
				 const char *name,
				 signed int adjust);

int request_profile_write(struct write_profile *head);

#endif
