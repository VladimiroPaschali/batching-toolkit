#include <linux/bpf.h>

#include <bpf/bpf_core_read.h>
#include <bpf/bpf_helpers.h>
#include <linux/if_ether.h>
#include <linux/ip.h>

struct {
  __uint(type, BPF_MAP_TYPE_PERCPU_ARRAY);
  __type(key, __u32);
  __type(value, __u64);
  __uint(max_entries, 1);
} counter SEC(".maps");

static __u64 max = 0;
static __u64 min = 0;

static __always_inline __u64 get_id(void *data, void *data_end) {
  struct ethhdr *eth = data;
  if ((void *)eth + sizeof(*eth) > data_end) {
    return 0;
  }

  char *buf = (char *)eth;
  __u32 id = buf[4] << 8 | buf[5];
  if (bpf_get_smp_processor_id() == 0) {
    //   __u64* value = 0;
    //   value = bpf_map_lookup_elem(&baddiers, &id);
    //   if (value) {
    //     bpf_printk("id: %x\n", id);
    //     *value += 1;
    //   } else {
    //     bpf_map_update_elem(&baddiers, &id, &value, BPF_ANY);
    //   }
    bpf_printk("id: %x\n", id);

    if (id > max) {
      max = id;
    }

    if (id < min || min == 0) {
      min = id;
    }
  }

  return 0;
}

SEC("xdp")
int cnt(struct xdp_md *ctx) {
  void *data_end = (void *)(long)ctx->data_end;
  void *data = (void *)(long)ctx->data;

  if (data + sizeof(struct ethhdr) > data_end) {
    return XDP_PASS;
  }

  __u64 id = get_id(data, data_end);
  // bpf_printk("id: %llx\n", id);
  __u32 key = 0;
  __u64 *value = bpf_map_lookup_elem(&counter, &key);
  if (value) {
    *value += 1;
  } else {
    bpf_printk("Failed to lookup key: %d\n", key);
  }
  return XDP_DROP;
}

char _license[] SEC("license") = "GPL";
