#include "prof_read.h"
#include <unistd.h>
#include <stdlib.h>
#include <assert.h>

void init_read_profiles(struct read_profile *head) {
  assert(head!=NULL);
  head->next=NULL;
  head->name="read";
}

struct read_profile *add_read_profile(struct read_profile *head,
				      const char *name) {
  struct read_profile *p;
  assert(head!=NULL);
  assert(name!=NULL);
  p=malloc(sizeof(struct read_profile));
  if (p==NULL)
    return p;
  p->name=malloc(strlen(name)+1);
  if (p->name==NULL) {
    free(p);
    return NULL;
  }
  strcpy(p->name, name);
  p->next=head->next;
  head->next=p;
  return p;
}


int remove_read_profile(struct read_profile *head, 
			const char *name) {
  struct read_profile *cur, **pprev;
  assert(head!=NULL);
  assert(name!=NULL);
  cur=head->next;
  pprev=&head->next;
  while (cur!=NULL) {
    assert(cur->name!=NULL);
    if (strcmp(cur->name,name)==0) {
      *pprev=cur->next;
      free(cur->name);
      free(cur);
      return 1;
    }
    pprev=&cur->next;
    cur=cur->next;
  }
  return 0;
}
