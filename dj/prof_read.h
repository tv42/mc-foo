#ifndef PROFILE_READ_H
#define PROFILE_READ_H

struct read_profile {
  struct read_profile *next;
  char *name;
};

void init_read_profiles(struct read_profile *head);
struct read_profile *add_read_profile(struct read_profile *head, 
				      const char *name);
int remove_read_profile(struct read_profile *head, 
			const char *name);

#endif
