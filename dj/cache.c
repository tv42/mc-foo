#include "playqueue.h"
#include <assert.h>

/*
 * try to ensure the queue has want playable songs,
 * but try at maximum max songs
 */
void request_caching_queuehead(struct playqueue *queue, int want, int max) {
  int n=0;
  struct queue_entry *cur;

  assert(queue);
  cur=queue->head;
  while(cur!=NULL && want>0 && n<=max) {
    if (!cur->song.media->cache.flags.mandatory
        && !cur->song.media->cache.flags.optional) {
      want--;
    } else if (cur->cache.state==done || cur->cache.state==request_failed) {
      want--;
    } else if (cur->cache.state==not_requested
        && (cur->song.media->cache.flags.mandatory
            || cur->song.media->cache.flags.optional)) {
      assert(cur->song.media->backend->cache.ops.request_cache!=NULL);
      cur->song.media->backend->cache.ops.request_cache(cur);
      cur->cache.state=requested;
    }
    n++;
    cur=cur->next;
  }
  /* want==0 if got as many as wanted */
}
