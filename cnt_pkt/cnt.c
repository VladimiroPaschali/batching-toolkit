#include "cnt.bpf.skel.h"
#include <bpf/bpf.h>
#include <bpf/libbpf.h>
#include <linux/bpf.h>
#include <net/if.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/resource.h>
#include <time.h>
#include <unistd.h>

int if_index;
struct cnt_bpf *cnt;

void sig_handler(int sig) {
  bpf_xdp_detach(if_index, 0, NULL);
  cnt_bpf__destroy(cnt);
  exit(0);
}

struct bss {
  __u64 max;
  __u64 min;
};

void bump_memlock_rlimit(void) {
  struct rlimit rlim_new = {
      .rlim_cur = RLIM_INFINITY,
      .rlim_max = RLIM_INFINITY,
  };

  if (setrlimit(RLIMIT_MEMLOCK, &rlim_new)) {
    fprintf(stderr, "Failed to increase RLIMIT_MEMLOCK limit!\n");
    exit(1);
  }
  if (setrlimit(RLIMIT_STACK, &rlim_new)) {
    fprintf(stderr, "Failed to increase RLIMIT_STACK limit!\n");
    exit(1);
  }
  if (setrlimit(RLIMIT_DATA, &rlim_new)) {
    fprintf(stderr, "Failed to increase RLIMIT_DATA limit!\n");
    exit(1);
  }
  if (setrlimit(RLIMIT_AS, &rlim_new)) {
    fprintf(stderr, "Failed to increase RLIMIT_AS limit!\n");
    exit(1);
  }
}
int main(int argc, char **argv) {

  int err;
  if (argc < 2) {
    fprintf(stderr, "Usage: %s <ifname>\n", argv[0]);
    return 1;
  }
  
  int n_core = 32;
  if (argc == 3) {
    n_core = atoi(argv[2]);
  }

  bump_memlock_rlimit();

  cnt = cnt_bpf__open_and_load();

  if (!cnt) {
    fprintf(stderr, "Failed to open and load BPF object\n");
    return 1;
  }

  if_index = if_nametoindex(argv[1]);
  if (!if_index) {
    fprintf(stderr, "Failed to get ifindex of %s\n", argv[1]);
    return 1;
  }
  err = bpf_xdp_attach(if_index, bpf_program__fd(cnt->progs.cnt), 0, NULL);
  if (err) {
    fprintf(stderr, "Failed to attach BPF program\n");
    return 1;
  }
  printf("BPF program attached\n");

  signal(SIGINT, sig_handler);
  signal(SIGTERM, sig_handler);
  signal(SIGKILL, sig_handler);
  signal(SIGPIPE, sig_handler);

  __u64 value[32];
  __u32 key = 0;
  struct bss bss = {0, 0};
  while (1) {
    sleep(1);
    __u64 total = 0;
    // lookup on percpu array
    if (bpf_map__lookup_elem(cnt->maps.counter, &key, sizeof(key), value,
                             sizeof(value), 0) != 0) {
      fprintf(stderr, "Failed to lookup key: %d\n", key);
      return 1;
    }

    if (bpf_map__lookup_elem(cnt->maps.bss, &key, sizeof(key), &bss,
                             sizeof(struct bss), 0) != 0) {
      fprintf(stderr, "Failed to lookup key: %d\n", key);
      return 1;
    }  

    for (int i = 0; i < n_core; i++) {
      total += value[i];
    }

    for (int i = 0; i < n_core; i++)
      fprintf(stderr, "core[%d]: %lld | %lld%%\n", i, value[i], value[i] * 100 / total);
    
    fprintf(stderr, "total: %lld\n", total);
    fprintf(stderr, "max: %llx\n", bss.max);
    fprintf(stderr, "min: %llx\n", bss.min);
  }

  return 0;
}
