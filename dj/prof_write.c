#include "prof_write.h"

#include <assert.h>

void init_write_profiles(struct write_profile *head) {
  assert(head!=NULL);
  head->next=NULL;
  head->name="write";
  head->scores=NULL;
}

struct write_profile *add_write_profile(struct write_profile *head, 
					const char *name) {
  struct write_profile *p;

  assert(head!=NULL);
  assert(name!=NULL);
  p=malloc(sizeof(struct write_profile));
  if (p==NULL)
    return NULL;
  p->name=malloc(strlen(name)+1);
  if (p->name==NULL) {
    free(p);
    return NULL;
  }
  strcpy(p->name, name);
  p->scores=NULL;
  p->next=head->next;
  head->next=p;
  return p;
}

struct write_profile *find_write_profile(struct write_profile *head, 
					 const char *name) {
  struct write_profile *cur=head;
  assert(head!=NULL);
  assert(name!=NULL);
  while (cur!=NULL) {
    assert(cur->name!=NULL);
    if (strcmp(cur->name, name)==0)
      break;
    cur=cur->next;
  }
  return cur;
}

struct score *add_score(struct write_profile *prof,
			const char *type,
			const char *name,
			signed int adjust) {
  struct score *s;
  assert(prof!=NULL);
  assert(type!=NULL);
  assert(name!=NULL);
  s=malloc(sizeof(struct score));
  if (s==NULL)
    return NULL;
  s->type=malloc(strlen(type)+1);
  if (s->type==NULL) {
    free(s);
    return NULL;
  }
  s->name=malloc(strlen(name)+1);
  if (s->name==NULL) {
    free(s->type);
    free(s);
    return NULL;
  }
  s->adjust=adjust;
  s->next=prof->scores;
  prof->scores=s;
  return s;
}

struct score *find_and_add_score(struct write_profile *head,
				 const char *prof,
				 const char *type,
				 const char *name,
				 signed int adjust) {
  struct write_profile *p;
  
  assert(head!=NULL);
  assert(prof!=NULL);
  assert(type!=NULL);
  assert(name!=NULL);

  p=find_write_profile(head, prof);
  if (p==NULL) {
    p=add_write_profile(head, prof);
    if (p==NULL)
      return NULL;
  }
  return add_score(p, type, name, adjust);
}

int request_profile_write(struct write_profile *head) {
  struct write_profile *cur;
  struct score *score;
  static time_t last_time=0;

  if (last_time!=0 && last_time > time(NULL)-20)
    return 0;
  
  last_time=time(NULL);

  cur=head;
  while (cur!=NULL) {
    score=cur->scores;
    while (score!=NULL) {
      if (write_to_child(queue->prof_write, cur->name, strlen(cur->name))==-1) {
	perror("dj: request_profile_write");
	return -1;
      }
      score=score->next;
    }
    cur=cur->next;
  }
  if (write_to_child(queue->prof_write, "\n", strlen("\n"))==-1) {
    perror("dj: request_profile_write");
    return -1;
  }
  return 0;
}
