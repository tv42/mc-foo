/*
 * try to ensure the queue has want playable songs,
 * but try at maximum max songs
 * returns:
 *  1: at least want songs playable
 *  0: not enough songs playable
 */
int request_caching_queuehead(struct playqueue *queue, int want, int max) {
  int n=0;
  struct queue_entry *cur;
  if (queue==NULL)
    return;
  cur=queue->head;
  while(cur!=NULL && want>0 && n<=max) {
    if (!cur->song.media->cache.flags.caching_mandatory
        && !cur->song.media->cache.flags.caching_optional) {
      want--;
    } else if (cur->cache.state==done) {
      want--;
    } else if (cur->cache.state==not_requested
        && (cur->song.media->cache.flags.caching_mandatory
            || cur->song.media->cache.flags.caching_optional)) {
      cur->song.media->backend->cache.request_cache(&cur->song);
      cur->cache.state=requested;
    }
    n++;
    cur=cur->next;
  }
  return want==0;
}
