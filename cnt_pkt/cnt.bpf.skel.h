/* SPDX-License-Identifier: (LGPL-2.1 OR BSD-2-Clause) */

/* THIS FILE IS AUTOGENERATED BY BPFTOOL! */
#ifndef __CNT_BPF_SKEL_H__
#define __CNT_BPF_SKEL_H__

#include <errno.h>
#include <stdlib.h>
#include <bpf/libbpf.h>

#define BPF_SKEL_SUPPORTS_MAP_AUTO_ATTACH 1

struct cnt_bpf {
	struct bpf_object_skeleton *skeleton;
	struct bpf_object *obj;
	struct {
		struct bpf_map *counter;
		struct bpf_map *rodata;
		struct bpf_map *bss;
	} maps;
	struct {
		struct bpf_program *cnt;
	} progs;
	struct {
		struct bpf_link *cnt;
	} links;

#ifdef __cplusplus
	static inline struct cnt_bpf *open(const struct bpf_object_open_opts *opts = nullptr);
	static inline struct cnt_bpf *open_and_load();
	static inline int load(struct cnt_bpf *skel);
	static inline int attach(struct cnt_bpf *skel);
	static inline void detach(struct cnt_bpf *skel);
	static inline void destroy(struct cnt_bpf *skel);
	static inline const void *elf_bytes(size_t *sz);
#endif /* __cplusplus */
};

static void
cnt_bpf__destroy(struct cnt_bpf *obj)
{
	if (!obj)
		return;
	if (obj->skeleton)
		bpf_object__destroy_skeleton(obj->skeleton);
	free(obj);
}

static inline int
cnt_bpf__create_skeleton(struct cnt_bpf *obj);

static inline struct cnt_bpf *
cnt_bpf__open_opts(const struct bpf_object_open_opts *opts)
{
	struct cnt_bpf *obj;
	int err;

	obj = (struct cnt_bpf *)calloc(1, sizeof(*obj));
	if (!obj) {
		errno = ENOMEM;
		return NULL;
	}

	err = cnt_bpf__create_skeleton(obj);
	if (err)
		goto err_out;

	err = bpf_object__open_skeleton(obj->skeleton, opts);
	if (err)
		goto err_out;

	return obj;
err_out:
	cnt_bpf__destroy(obj);
	errno = -err;
	return NULL;
}

static inline struct cnt_bpf *
cnt_bpf__open(void)
{
	return cnt_bpf__open_opts(NULL);
}

static inline int
cnt_bpf__load(struct cnt_bpf *obj)
{
	return bpf_object__load_skeleton(obj->skeleton);
}

static inline struct cnt_bpf *
cnt_bpf__open_and_load(void)
{
	struct cnt_bpf *obj;
	int err;

	obj = cnt_bpf__open();
	if (!obj)
		return NULL;
	err = cnt_bpf__load(obj);
	if (err) {
		cnt_bpf__destroy(obj);
		errno = -err;
		return NULL;
	}
	return obj;
}

static inline int
cnt_bpf__attach(struct cnt_bpf *obj)
{
	return bpf_object__attach_skeleton(obj->skeleton);
}

static inline void
cnt_bpf__detach(struct cnt_bpf *obj)
{
	bpf_object__detach_skeleton(obj->skeleton);
}

static inline const void *cnt_bpf__elf_bytes(size_t *sz);

static inline int
cnt_bpf__create_skeleton(struct cnt_bpf *obj)
{
	struct bpf_object_skeleton *s;
	struct bpf_map_skeleton *map __attribute__((unused));
	int err;

	s = (struct bpf_object_skeleton *)calloc(1, sizeof(*s));
	if (!s)	{
		err = -ENOMEM;
		goto err;
	}

	s->sz = sizeof(*s);
	s->name = "cnt_bpf";
	s->obj = &obj->obj;

	/* maps */
	s->map_cnt = 3;
	s->map_skel_sz = 24;
	s->maps = (struct bpf_map_skeleton *)calloc(s->map_cnt,
			sizeof(*s->maps) > 24 ? sizeof(*s->maps) : 24);
	if (!s->maps) {
		err = -ENOMEM;
		goto err;
	}

	map = (struct bpf_map_skeleton *)((char *)s->maps + 0 * s->map_skel_sz);
	map->name = "counter";
	map->map = &obj->maps.counter;

	map = (struct bpf_map_skeleton *)((char *)s->maps + 1 * s->map_skel_sz);
	map->name = "cnt_bpf.rodata";
	map->map = &obj->maps.rodata;

	map = (struct bpf_map_skeleton *)((char *)s->maps + 2 * s->map_skel_sz);
	map->name = "cnt_bpf.bss";
	map->map = &obj->maps.bss;

	/* programs */
	s->prog_cnt = 1;
	s->prog_skel_sz = sizeof(*s->progs);
	s->progs = (struct bpf_prog_skeleton *)calloc(s->prog_cnt, s->prog_skel_sz);
	if (!s->progs) {
		err = -ENOMEM;
		goto err;
	}

	s->progs[0].name = "cnt";
	s->progs[0].prog = &obj->progs.cnt;
	s->progs[0].link = &obj->links.cnt;

	s->data = cnt_bpf__elf_bytes(&s->data_sz);

	obj->skeleton = s;
	return 0;
err:
	bpf_object__destroy_skeleton(s);
	return err;
}

static inline const void *cnt_bpf__elf_bytes(size_t *sz)
{
	static const char data[] __attribute__((__aligned__(8))) = "\
\x7f\x45\x4c\x46\x02\x01\x01\0\0\0\0\0\0\0\0\0\x01\0\xf7\0\x01\0\0\0\0\0\0\0\0\
\0\0\0\0\0\0\0\0\0\0\0\x90\x1f\0\0\0\0\0\0\0\0\0\0\x40\0\0\0\0\0\x40\0\x1d\0\
\x01\0\xb7\0\0\0\x02\0\0\0\x61\x12\x04\0\0\0\0\0\x61\x11\0\0\0\0\0\0\xbf\x13\0\
\0\0\0\0\0\x07\x03\0\0\x0e\0\0\0\x2d\x23\x30\0\0\0\0\0\x71\x17\x05\0\0\0\0\0\
\x71\x16\x04\0\0\0\0\0\x85\0\0\0\x08\0\0\0\x67\0\0\0\x20\0\0\0\x77\0\0\0\x20\0\
\0\0\x55\0\x18\0\0\0\0\0\x67\x07\0\0\x38\0\0\0\xc7\x07\0\0\x38\0\0\0\x67\x06\0\
\0\x38\0\0\0\xc7\x06\0\0\x38\0\0\0\x67\x06\0\0\x08\0\0\0\x4f\x76\0\0\0\0\0\0\
\x18\x01\0\0\x1a\0\0\0\0\0\0\0\0\0\0\0\xb7\x02\0\0\x08\0\0\0\xbf\x63\0\0\0\0\0\
\0\x85\0\0\0\x06\0\0\0\x67\x06\0\0\x20\0\0\0\x77\x06\0\0\x20\0\0\0\x18\x01\0\0\
\0\0\0\0\0\0\0\0\0\0\0\0\x79\x12\0\0\0\0\0\0\x3d\x62\x01\0\0\0\0\0\x7b\x61\0\0\
\0\0\0\0\x18\x01\0\0\x08\0\0\0\0\0\0\0\0\0\0\0\x79\x12\0\0\0\0\0\0\x07\x02\0\0\
\xff\xff\xff\xff\x2d\x26\x01\0\0\0\0\0\x7b\x61\0\0\0\0\0\0\xb7\x01\0\0\0\0\0\0\
\x63\x1a\xfc\xff\0\0\0\0\xbf\xa2\0\0\0\0\0\0\x07\x02\0\0\xfc\xff\xff\xff\x18\
\x01\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x85\0\0\0\x01\0\0\0\x15\0\x04\0\0\0\0\0\x79\
\x01\0\0\0\0\0\0\x07\x01\0\0\x01\0\0\0\x7b\x10\0\0\0\0\0\0\x05\0\x05\0\0\0\0\0\
\x61\xa3\xfc\xff\0\0\0\0\x18\x01\0\0\0\0\0\0\0\0\0\0\0\0\0\0\xb7\x02\0\0\x1a\0\
\0\0\x85\0\0\0\x06\0\0\0\xb7\0\0\0\x01\0\0\0\x95\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\
\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x46\x61\x69\x6c\x65\x64\x20\
\x74\x6f\x20\x6c\x6f\x6f\x6b\x75\x70\x20\x6b\x65\x79\x3a\x20\x25\x64\x0a\0\x69\
\x64\x3a\x20\x25\x78\x0a\0\x47\x50\x4c\0\0\0\x6f\0\0\0\x05\0\x08\0\x06\0\0\0\
\x18\0\0\0\x1e\0\0\0\x24\0\0\0\x2a\0\0\0\x56\0\0\0\x5f\0\0\0\x04\0\x18\x01\x51\
\0\x04\x10\x48\x01\x52\0\x04\x18\x48\x01\x51\0\x04\x80\x01\x88\x01\x12\x76\0\
\x38\x24\x77\0\xa8\xa7\x80\x80\0\xa8\xab\x80\x80\0\x21\x9f\x04\x88\x01\x90\x01\
\x06\x76\0\x77\0\x21\x9f\x04\x90\x01\xc0\x01\x01\x56\0\x04\xa0\x02\xb0\x03\x02\
\x30\x9f\0\x04\xd8\x02\xa8\x03\x01\x50\0\x01\x11\x01\x25\x25\x13\x05\x03\x25\
\x72\x17\x10\x17\x1b\x25\x11\x1b\x12\x06\x73\x17\x8c\x01\x17\0\0\x02\x24\0\x03\
\x25\x3e\x0b\x0b\x0b\0\0\x03\x2e\x01\x11\x1b\x12\x06\x40\x18\x7a\x19\x03\x25\
\x3a\x0b\x3b\x0b\x27\x19\x49\x13\x3f\x19\0\0\x04\x34\0\x03\x25\x49\x13\x3a\x0b\
\x3b\x0b\x02\x18\0\0\x05\x05\0\x02\x22\x03\x25\x3a\x0b\x3b\x0b\x49\x13\0\0\x06\
\x34\0\x02\x18\x03\x25\x3a\x0b\x3b\x0b\x49\x13\0\0\x07\x34\0\x02\x22\x03\x25\
\x3a\x0b\x3b\x0b\x49\x13\0\0\x08\x1d\x01\x31\x13\x11\x1b\x12\x06\x58\x0b\x59\
\x0b\x57\x0b\0\0\x09\x34\0\x02\x22\x31\x13\0\0\x0a\x01\x01\x49\x13\0\0\x0b\x21\
\0\x49\x13\x37\x0b\0\0\x0c\x26\0\x49\x13\0\0\x0d\x24\0\x03\x25\x0b\x0b\x3e\x0b\
\0\0\x0e\x34\0\x03\x25\x49\x13\x3f\x19\x3a\x0b\x3b\x0b\x02\x18\0\0\x0f\x13\x01\
\x0b\x0b\x3a\x0b\x3b\x0b\0\0\x10\x0d\0\x03\x25\x49\x13\x3a\x0b\x3b\x0b\x38\x0b\
\0\0\x11\x0f\0\x49\x13\0\0\x12\x16\0\x49\x13\x03\x25\x3a\x0b\x3b\x0b\0\0\x13\
\x2e\x01\0\0\x14\x34\0\x03\x25\x49\x13\x3a\x0b\x3b\x0b\x1c\x0f\0\0\x15\x15\0\
\x49\x13\x27\x19\0\0\x16\x15\x01\x49\x13\x27\x19\0\0\x17\x05\0\x49\x13\0\0\x18\
\x0f\0\0\0\x19\x26\0\0\0\x1a\x18\0\0\0\x1b\x04\x01\x49\x13\x03\x25\x0b\x0b\x3a\
\x0b\x3b\x05\0\0\x1c\x28\0\x03\x25\x1c\x0f\0\0\x1d\x2e\x01\x03\x25\x3a\x0b\x3b\
\x0b\x27\x19\x49\x13\x20\x21\x01\0\0\x1e\x05\0\x03\x25\x3a\x0b\x3b\x0b\x49\x13\
\0\0\x1f\x34\0\x03\x25\x3a\x0b\x3b\x0b\x49\x13\0\0\x20\x13\x01\x03\x25\x0b\x0b\
\x3a\x0b\x3b\x0b\0\0\x21\x13\x01\x03\x25\x0b\x0b\x3a\x0b\x3b\x05\0\0\x22\x0d\0\
\x03\x25\x49\x13\x3a\x0b\x3b\x05\x38\x0b\0\0\0\xb0\x02\0\0\x05\0\x01\x08\0\0\0\
\0\x01\0\x1d\0\x01\x08\0\0\0\0\0\0\0\x02\x06\xb8\x01\0\0\x08\0\0\0\x0c\0\0\0\
\x02\x2c\x05\x01\x02\x2b\x05\x04\x03\x06\xb8\x01\0\0\x01\x5a\x2d\0\x32\x0b\x01\
\0\0\x04\x03\x96\0\0\0\0\x41\x02\xa1\0\x05\0\x2e\0\x32\x6b\x02\0\0\x06\x02\x91\
\x04\x0a\0\x3c\x14\x01\0\0\x07\x01\x1f\0\x33\xa2\x01\0\0\x07\x02\x1e\0\x34\xa2\
\x01\0\0\x07\x04\x20\0\x3a\x25\x01\0\0\x07\x05\x0d\0\x3d\x20\x01\0\0\x08\xf0\
\x01\0\0\x07\xf0\0\0\0\0\x3a\x0e\x09\x03\x08\x02\0\0\0\0\x0a\xa2\0\0\0\x0b\xab\
\0\0\0\x1a\0\x0c\xa7\0\0\0\x02\x04\x06\x01\x0d\x05\x08\x07\x0e\x06\xba\0\0\0\0\
\x46\x02\xa1\x01\x0a\xa7\0\0\0\x0b\xab\0\0\0\x04\0\x0e\x07\xd1\0\0\0\0\x0d\x02\
\xa1\x02\x0f\x20\0\x08\x10\x08\xfa\0\0\0\0\x09\0\x10\x0a\x0f\x01\0\0\0\x0a\x08\
\x10\x0d\x20\x01\0\0\0\x0b\x10\x10\x10\x31\x01\0\0\0\x0c\x18\0\x11\xff\0\0\0\
\x0a\x0b\x01\0\0\x0b\xab\0\0\0\x06\0\x02\x09\x05\x04\x11\x14\x01\0\0\x12\x1c\
\x01\0\0\x0c\x01\x1b\x02\x0b\x07\x04\x11\x25\x01\0\0\x12\x2d\x01\0\0\x0f\x01\
\x1f\x02\x0e\x07\x08\x11\x36\x01\0\0\x0a\x0b\x01\0\0\x0b\xab\0\0\0\x01\0\x13\
\x04\x03\x4f\x01\0\0\0\x23\x02\xa1\x03\0\x0a\xa2\0\0\0\x0b\xab\0\0\0\x08\0\x14\
\x11\x64\x01\0\0\x02\xce\x08\x11\x69\x01\0\0\x15\x14\x01\0\0\x04\x12\x25\x01\0\
\0\0\x0f\x02\xa1\x04\x04\x13\x25\x01\0\0\0\x10\x02\xa1\x05\x14\x14\x8d\x01\0\0\
\x02\x38\x01\x11\x92\x01\0\0\x16\xa2\x01\0\0\x17\xa2\x01\0\0\x17\xa3\x01\0\0\0\
\x18\x11\xa8\x01\0\0\x19\x14\x15\xb2\x01\0\0\x02\xb1\x06\x11\xb7\x01\0\0\x16\
\xc8\x01\0\0\x17\xcc\x01\0\0\x17\x14\x01\0\0\x1a\0\x02\x16\x05\x08\x11\xa2\0\0\
\0\x1b\x1c\x01\0\0\x1c\x04\x03\xc1\x18\x1c\x17\0\x1c\x18\x01\x1c\x19\x02\x1c\
\x1a\x03\x1c\x1b\x04\0\x11\xa7\0\0\0\x1d\x1d\0\x12\x25\x01\0\0\x1e\x1e\0\x12\
\xa2\x01\0\0\x1e\x1f\0\x12\xa2\x01\0\0\x1f\x20\0\x19\x14\x01\0\0\x1f\x21\0\x13\
\x21\x02\0\0\x1f\x2a\0\x18\xeb\x01\0\0\0\x11\x26\x02\0\0\x20\x29\x0e\x04\xad\
\x10\x22\x47\x02\0\0\x04\xae\0\x10\x24\x47\x02\0\0\x04\xaf\x06\x10\x25\x57\x02\
\0\0\x04\xb0\x0c\0\x0a\x53\x02\0\0\x0b\xab\0\0\0\x06\0\x02\x23\x08\x01\x12\x5f\
\x02\0\0\x28\x05\x20\x12\x67\x02\0\0\x27\x01\x18\x02\x26\x07\x02\x11\x70\x02\0\
\0\x21\x33\x18\x03\xcc\x18\x22\x1e\x14\x01\0\0\x03\xcd\x18\0\x22\x1f\x14\x01\0\
\0\x03\xce\x18\x04\x22\x2f\x14\x01\0\0\x03\xcf\x18\x08\x22\x30\x14\x01\0\0\x03\
\xd1\x18\x0c\x22\x31\x14\x01\0\0\x03\xd2\x18\x10\x22\x32\x14\x01\0\0\x03\xd4\
\x18\x14\0\0\xd4\0\0\0\x05\0\0\0\0\0\0\0\x27\0\0\0\x31\0\0\0\x5a\0\0\0\x62\0\0\
\0\x67\0\0\0\x7b\0\0\0\x84\0\0\0\x8c\0\0\0\x91\0\0\0\x95\0\0\0\x99\0\0\0\xa6\0\
\0\0\xac\0\0\0\xb2\0\0\0\xc5\0\0\0\xcb\0\0\0\xd7\0\0\0\xf0\0\0\0\xf4\0\0\0\xf8\
\0\0\0\x0c\x01\0\0\x1d\x01\0\0\x22\x01\0\0\x2e\x01\0\0\x37\x01\0\0\x40\x01\0\0\
\x47\x01\0\0\x54\x01\0\0\x5f\x01\0\0\x66\x01\0\0\x6b\x01\0\0\x74\x01\0\0\x77\
\x01\0\0\x7b\x01\0\0\x82\x01\0\0\x90\x01\0\0\x99\x01\0\0\xa1\x01\0\0\xb0\x01\0\
\0\xb6\x01\0\0\xbd\x01\0\0\xc4\x01\0\0\xc8\x01\0\0\xd9\x01\0\0\xe9\x01\0\0\xed\
\x01\0\0\xf1\x01\0\0\xfb\x01\0\0\x0b\x02\0\0\x1a\x02\0\0\x29\x02\0\0\x55\x62\
\x75\x6e\x74\x75\x20\x63\x6c\x61\x6e\x67\x20\x76\x65\x72\x73\x69\x6f\x6e\x20\
\x31\x38\x2e\x31\x2e\x33\x20\x28\x31\x75\x62\x75\x6e\x74\x75\x31\x29\0\x63\x6e\
\x74\x2e\x62\x70\x66\x2e\x63\0\x2f\x68\x6f\x6d\x65\x2f\x76\x6c\x61\x64\x69\x6d\
\x69\x72\x6f\x2f\x62\x61\x74\x63\x68\x69\x6e\x67\x2d\x74\x6f\x6f\x6c\x6b\x69\
\x74\x2f\x63\x6e\x74\x5f\x70\x6b\x74\0\x5f\x5f\x5f\x5f\x66\x6d\x74\0\x63\x68\
\x61\x72\0\x5f\x5f\x41\x52\x52\x41\x59\x5f\x53\x49\x5a\x45\x5f\x54\x59\x50\x45\
\x5f\x5f\0\x5f\x6c\x69\x63\x65\x6e\x73\x65\0\x63\x6f\x75\x6e\x74\x65\x72\0\x74\
\x79\x70\x65\0\x69\x6e\x74\0\x6b\x65\x79\0\x75\x6e\x73\x69\x67\x6e\x65\x64\x20\
\x69\x6e\x74\0\x5f\x5f\x75\x33\x32\0\x76\x61\x6c\x75\x65\0\x75\x6e\x73\x69\x67\
\x6e\x65\x64\x20\x6c\x6f\x6e\x67\x20\x6c\x6f\x6e\x67\0\x5f\x5f\x75\x36\x34\0\
\x6d\x61\x78\x5f\x65\x6e\x74\x72\x69\x65\x73\0\x62\x70\x66\x5f\x67\x65\x74\x5f\
\x73\x6d\x70\x5f\x70\x72\x6f\x63\x65\x73\x73\x6f\x72\x5f\x69\x64\0\x6d\x61\x78\
\0\x6d\x69\x6e\0\x62\x70\x66\x5f\x6d\x61\x70\x5f\x6c\x6f\x6f\x6b\x75\x70\x5f\
\x65\x6c\x65\x6d\0\x62\x70\x66\x5f\x74\x72\x61\x63\x65\x5f\x70\x72\x69\x6e\x74\
\x6b\0\x6c\x6f\x6e\x67\0\x58\x44\x50\x5f\x41\x42\x4f\x52\x54\x45\x44\0\x58\x44\
\x50\x5f\x44\x52\x4f\x50\0\x58\x44\x50\x5f\x50\x41\x53\x53\0\x58\x44\x50\x5f\
\x54\x58\0\x58\x44\x50\x5f\x52\x45\x44\x49\x52\x45\x43\x54\0\x78\x64\x70\x5f\
\x61\x63\x74\x69\x6f\x6e\0\x67\x65\x74\x5f\x69\x64\0\x64\x61\x74\x61\0\x64\x61\
\x74\x61\x5f\x65\x6e\x64\0\x69\x64\0\x65\x74\x68\0\x68\x5f\x64\x65\x73\x74\0\
\x75\x6e\x73\x69\x67\x6e\x65\x64\x20\x63\x68\x61\x72\0\x68\x5f\x73\x6f\x75\x72\
\x63\x65\0\x68\x5f\x70\x72\x6f\x74\x6f\0\x75\x6e\x73\x69\x67\x6e\x65\x64\x20\
\x73\x68\x6f\x72\x74\0\x5f\x5f\x75\x31\x36\0\x5f\x5f\x62\x65\x31\x36\0\x65\x74\
\x68\x68\x64\x72\0\x62\x75\x66\0\x44\x57\x5f\x41\x54\x45\x5f\x73\x69\x67\x6e\
\x65\x64\x5f\x33\x32\0\x44\x57\x5f\x41\x54\x45\x5f\x73\x69\x67\x6e\x65\x64\x5f\
\x38\0\x63\x6e\x74\0\x63\x74\x78\0\x64\x61\x74\x61\x5f\x6d\x65\x74\x61\0\x69\
\x6e\x67\x72\x65\x73\x73\x5f\x69\x66\x69\x6e\x64\x65\x78\0\x72\x78\x5f\x71\x75\
\x65\x75\x65\x5f\x69\x6e\x64\x65\x78\0\x65\x67\x72\x65\x73\x73\x5f\x69\x66\x69\
\x6e\x64\x65\x78\0\x78\x64\x70\x5f\x6d\x64\0\x44\0\0\0\x05\0\x08\0\0\0\0\0\0\0\
\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x1a\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x08\0\0\
\0\0\0\0\0\0\0\0\0\0\0\0\0\x30\0\0\0\0\0\0\0\0\0\x9f\xeb\x01\0\x18\0\0\0\0\0\0\
\0\xb0\x02\0\0\xb0\x02\0\0\x43\x03\0\0\0\0\0\0\0\0\0\x02\x03\0\0\0\x01\0\0\0\0\
\0\0\x01\x04\0\0\0\x20\0\0\x01\0\0\0\0\0\0\0\x03\0\0\0\0\x02\0\0\0\x04\0\0\0\
\x06\0\0\0\x05\0\0\0\0\0\0\x01\x04\0\0\0\x20\0\0\0\0\0\0\0\0\0\0\x02\x06\0\0\0\
\x19\0\0\0\0\0\0\x08\x07\0\0\0\x1f\0\0\0\0\0\0\x01\x04\0\0\0\x20\0\0\0\0\0\0\0\
\0\0\0\x02\x09\0\0\0\x2c\0\0\0\0\0\0\x08\x0a\0\0\0\x32\0\0\0\0\0\0\x01\x08\0\0\
\0\x40\0\0\0\0\0\0\0\0\0\0\x02\x0c\0\0\0\0\0\0\0\0\0\0\x03\0\0\0\0\x02\0\0\0\
\x04\0\0\0\x01\0\0\0\0\0\0\0\x04\0\0\x04\x20\0\0\0\x45\0\0\0\x01\0\0\0\0\0\0\0\
\x4a\0\0\0\x05\0\0\0\x40\0\0\0\x4e\0\0\0\x08\0\0\0\x80\0\0\0\x54\0\0\0\x0b\0\0\
\0\xc0\0\0\0\x60\0\0\0\0\0\0\x0e\x0d\0\0\0\x01\0\0\0\0\0\0\0\0\0\0\x02\x10\0\0\
\0\x68\0\0\0\x06\0\0\x04\x18\0\0\0\x6f\0\0\0\x06\0\0\0\0\0\0\0\x74\0\0\0\x06\0\
\0\0\x20\0\0\0\x7d\0\0\0\x06\0\0\0\x40\0\0\0\x87\0\0\0\x06\0\0\0\x60\0\0\0\x97\
\0\0\0\x06\0\0\0\x80\0\0\0\xa6\0\0\0\x06\0\0\0\xa0\0\0\0\0\0\0\0\x01\0\0\x0d\
\x02\0\0\0\xb5\0\0\0\x0f\0\0\0\xb9\0\0\0\x01\0\0\x0c\x11\0\0\0\0\0\0\0\0\0\0\
\x0a\x14\0\0\0\xf7\x02\0\0\0\0\0\x01\x01\0\0\0\x08\0\0\x01\0\0\0\0\0\0\0\x03\0\
\0\0\0\x13\0\0\0\x04\0\0\0\x1a\0\0\0\xfc\x02\0\0\0\0\0\x0e\x15\0\0\0\0\0\0\0\0\
\0\0\0\0\0\0\x03\0\0\0\0\x14\0\0\0\x04\0\0\0\x04\0\0\0\x08\x03\0\0\0\0\0\x0e\
\x17\0\0\0\x01\0\0\0\0\0\0\0\0\0\0\x03\0\0\0\0\x13\0\0\0\x04\0\0\0\x08\0\0\0\
\x11\x03\0\0\0\0\0\x0e\x19\0\0\0\0\0\0\0\x20\x03\0\0\0\0\0\x0e\x09\0\0\0\0\0\0\
\0\x24\x03\0\0\0\0\0\x0e\x09\0\0\0\0\0\0\0\x28\x03\0\0\x02\0\0\x0f\0\0\0\0\x1b\
\0\0\0\0\0\0\0\x08\0\0\0\x1c\0\0\0\x08\0\0\0\x08\0\0\0\x2d\x03\0\0\x01\0\0\x0f\
\0\0\0\0\x0e\0\0\0\0\0\0\0\x20\0\0\0\x33\x03\0\0\x02\0\0\x0f\0\0\0\0\x16\0\0\0\
\0\0\0\0\x1a\0\0\0\x1a\0\0\0\x1a\0\0\0\x08\0\0\0\x3b\x03\0\0\x01\0\0\x0f\0\0\0\
\0\x18\0\0\0\0\0\0\0\x04\0\0\0\0\x69\x6e\x74\0\x5f\x5f\x41\x52\x52\x41\x59\x5f\
\x53\x49\x5a\x45\x5f\x54\x59\x50\x45\x5f\x5f\0\x5f\x5f\x75\x33\x32\0\x75\x6e\
\x73\x69\x67\x6e\x65\x64\x20\x69\x6e\x74\0\x5f\x5f\x75\x36\x34\0\x75\x6e\x73\
\x69\x67\x6e\x65\x64\x20\x6c\x6f\x6e\x67\x20\x6c\x6f\x6e\x67\0\x74\x79\x70\x65\
\0\x6b\x65\x79\0\x76\x61\x6c\x75\x65\0\x6d\x61\x78\x5f\x65\x6e\x74\x72\x69\x65\
\x73\0\x63\x6f\x75\x6e\x74\x65\x72\0\x78\x64\x70\x5f\x6d\x64\0\x64\x61\x74\x61\
\0\x64\x61\x74\x61\x5f\x65\x6e\x64\0\x64\x61\x74\x61\x5f\x6d\x65\x74\x61\0\x69\
\x6e\x67\x72\x65\x73\x73\x5f\x69\x66\x69\x6e\x64\x65\x78\0\x72\x78\x5f\x71\x75\
\x65\x75\x65\x5f\x69\x6e\x64\x65\x78\0\x65\x67\x72\x65\x73\x73\x5f\x69\x66\x69\
\x6e\x64\x65\x78\0\x63\x74\x78\0\x63\x6e\x74\0\x78\x64\x70\0\x2f\x68\x6f\x6d\
\x65\x2f\x76\x6c\x61\x64\x69\x6d\x69\x72\x6f\x2f\x62\x61\x74\x63\x68\x69\x6e\
\x67\x2d\x74\x6f\x6f\x6c\x6b\x69\x74\x2f\x63\x6e\x74\x5f\x70\x6b\x74\x2f\x63\
\x6e\x74\x2e\x62\x70\x66\x2e\x63\0\x69\x6e\x74\x20\x63\x6e\x74\x28\x73\x74\x72\
\x75\x63\x74\x20\x78\x64\x70\x5f\x6d\x64\x20\x2a\x63\x74\x78\x29\x20\x7b\0\x20\
\x20\x76\x6f\x69\x64\x20\x2a\x64\x61\x74\x61\x5f\x65\x6e\x64\x20\x3d\x20\x28\
\x76\x6f\x69\x64\x20\x2a\x29\x28\x6c\x6f\x6e\x67\x29\x63\x74\x78\x2d\x3e\x64\
\x61\x74\x61\x5f\x65\x6e\x64\x3b\0\x20\x20\x76\x6f\x69\x64\x20\x2a\x64\x61\x74\
\x61\x20\x3d\x20\x28\x76\x6f\x69\x64\x20\x2a\x29\x28\x6c\x6f\x6e\x67\x29\x63\
\x74\x78\x2d\x3e\x64\x61\x74\x61\x3b\0\x20\x20\x69\x66\x20\x28\x64\x61\x74\x61\
\x20\x2b\x20\x73\x69\x7a\x65\x6f\x66\x28\x73\x74\x72\x75\x63\x74\x20\x65\x74\
\x68\x68\x64\x72\x29\x20\x3e\x20\x64\x61\x74\x61\x5f\x65\x6e\x64\x29\x20\x7b\0\
\x20\x20\x5f\x5f\x75\x33\x32\x20\x69\x64\x20\x3d\x20\x62\x75\x66\x5b\x34\x5d\
\x20\x3c\x3c\x20\x38\x20\x7c\x20\x62\x75\x66\x5b\x35\x5d\x3b\0\x20\x20\x69\x66\
\x20\x28\x62\x70\x66\x5f\x67\x65\x74\x5f\x73\x6d\x70\x5f\x70\x72\x6f\x63\x65\
\x73\x73\x6f\x72\x5f\x69\x64\x28\x29\x20\x3d\x3d\x20\x30\x29\x20\x7b\0\x20\x20\
\x20\x20\x62\x70\x66\x5f\x70\x72\x69\x6e\x74\x6b\x28\x22\x69\x64\x3a\x20\x25\
\x78\x5c\x6e\x22\x2c\x20\x69\x64\x29\x3b\0\x20\x20\x20\x20\x69\x66\x20\x28\x69\
\x64\x20\x3e\x20\x6d\x61\x78\x29\x20\x7b\0\x20\x20\x20\x20\x20\x20\x6d\x61\x78\
\x20\x3d\x20\x69\x64\x3b\0\x20\x20\x20\x20\x69\x66\x20\x28\x69\x64\x20\x3c\x20\
\x6d\x69\x6e\x20\x7c\x7c\x20\x6d\x69\x6e\x20\x3d\x3d\x20\x30\x29\x20\x7b\0\x20\
\x20\x20\x20\x20\x20\x6d\x69\x6e\x20\x3d\x20\x69\x64\x3b\0\x20\x20\x5f\x5f\x75\
\x33\x32\x20\x6b\x65\x79\x20\x3d\x20\x30\x3b\0\x20\x20\x5f\x5f\x75\x36\x34\x20\
\x2a\x76\x61\x6c\x75\x65\x20\x3d\x20\x62\x70\x66\x5f\x6d\x61\x70\x5f\x6c\x6f\
\x6f\x6b\x75\x70\x5f\x65\x6c\x65\x6d\x28\x26\x63\x6f\x75\x6e\x74\x65\x72\x2c\
\x20\x26\x6b\x65\x79\x29\x3b\0\x20\x20\x69\x66\x20\x28\x76\x61\x6c\x75\x65\x29\
\x20\x7b\0\x20\x20\x20\x20\x2a\x76\x61\x6c\x75\x65\x20\x2b\x3d\x20\x31\x3b\0\
\x20\x20\x20\x20\x62\x70\x66\x5f\x70\x72\x69\x6e\x74\x6b\x28\x22\x46\x61\x69\
\x6c\x65\x64\x20\x74\x6f\x20\x6c\x6f\x6f\x6b\x75\x70\x20\x6b\x65\x79\x3a\x20\
\x25\x64\x5c\x6e\x22\x2c\x20\x6b\x65\x79\x29\x3b\0\x7d\0\x63\x68\x61\x72\0\x63\
\x6e\x74\x2e\x5f\x5f\x5f\x5f\x66\x6d\x74\0\x5f\x6c\x69\x63\x65\x6e\x73\x65\0\
\x67\x65\x74\x5f\x69\x64\x2e\x5f\x5f\x5f\x5f\x66\x6d\x74\0\x6d\x61\x78\0\x6d\
\x69\x6e\0\x2e\x62\x73\x73\0\x2e\x6d\x61\x70\x73\0\x2e\x72\x6f\x64\x61\x74\x61\
\0\x6c\x69\x63\x65\x6e\x73\x65\0\0\x9f\xeb\x01\0\x20\0\0\0\0\0\0\0\x14\0\0\0\
\x14\0\0\0\xcc\x01\0\0\xe0\x01\0\0\0\0\0\0\x08\0\0\0\xbd\0\0\0\x01\0\0\0\0\0\0\
\0\x12\0\0\0\x10\0\0\0\xbd\0\0\0\x1c\0\0\0\0\0\0\0\xc1\0\0\0\xf4\0\0\0\0\xc8\0\
\0\x08\0\0\0\xc1\0\0\0\x12\x01\0\0\x27\xcc\0\0\x10\0\0\0\xc1\0\0\0\x42\x01\0\0\
\x23\xd0\0\0\x18\0\0\0\xc1\0\0\0\x6a\x01\0\0\x0c\xd8\0\0\x28\0\0\0\xc1\0\0\0\
\x6a\x01\0\0\x07\xd8\0\0\x30\0\0\0\xc1\0\0\0\x9b\x01\0\0\x1c\x64\0\0\x38\0\0\0\
\xc1\0\0\0\x9b\x01\0\0\x0e\x64\0\0\x40\0\0\0\xc1\0\0\0\xbe\x01\0\0\x07\x68\0\0\
\x58\0\0\0\xc1\0\0\0\xbe\x01\0\0\x07\x68\0\0\x60\0\0\0\xc1\0\0\0\x9b\x01\0\0\
\x1c\x64\0\0\x70\0\0\0\xc1\0\0\0\x9b\x01\0\0\x0e\x64\0\0\x80\0\0\0\xc1\0\0\0\
\x9b\x01\0\0\x15\x64\0\0\x88\0\0\0\xc1\0\0\0\x9b\x01\0\0\x1a\x64\0\0\x90\0\0\0\
\xc1\0\0\0\xe7\x01\0\0\x05\x8c\0\0\xb8\0\0\0\xc1\0\0\0\x07\x02\0\0\x09\x94\0\0\
\xc8\0\0\0\xc1\0\0\0\x07\x02\0\0\x0e\x94\0\0\xe0\0\0\0\xc1\0\0\0\x07\x02\0\0\
\x09\x94\0\0\xe8\0\0\0\xc1\0\0\0\x1b\x02\0\0\x0b\x98\0\0\xf0\0\0\0\xc1\0\0\0\
\x2b\x02\0\0\x0e\xa4\0\0\x08\x01\0\0\xc1\0\0\0\x2b\x02\0\0\x12\xa4\0\0\x18\x01\
\0\0\xc1\0\0\0\x4b\x02\0\0\x0b\xa8\0\0\x28\x01\0\0\xc1\0\0\0\x5b\x02\0\0\x09\
\xf0\0\0\x38\x01\0\0\xc1\0\0\0\0\0\0\0\0\0\0\0\x40\x01\0\0\xc1\0\0\0\x6c\x02\0\
\0\x12\xf4\0\0\x58\x01\0\0\xc1\0\0\0\xa2\x02\0\0\x07\xf8\0\0\x60\x01\0\0\xc1\0\
\0\0\xb1\x02\0\0\x0c\xfc\0\0\x80\x01\0\0\xc1\0\0\0\xc2\x02\0\0\x05\x04\x01\0\
\xb0\x01\0\0\xc1\0\0\0\xf5\x02\0\0\x01\x10\x01\0\0\0\0\0\x0c\0\0\0\xff\xff\xff\
\xff\x04\0\x08\0\x08\x7c\x0b\0\x14\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\xb8\x01\0\0\0\
\0\0\0\x3f\x01\0\0\x05\0\x08\0\xac\0\0\0\x08\x01\x01\xfb\x0e\x0d\0\x01\x01\x01\
\x01\0\0\0\x01\0\0\x01\x01\x01\x1f\x04\0\0\0\0\x29\0\0\0\x42\0\0\0\x53\0\0\0\
\x03\x01\x1f\x02\x0f\x05\x1e\x06\x66\0\0\0\0\x4d\x20\xde\x67\xfb\x56\x2f\x6e\
\x7e\xcf\x28\x62\x2d\x7a\x86\xaf\x70\0\0\0\x01\xb8\x10\xf2\x70\x73\x3e\x10\x63\
\x19\xb6\x7e\xf5\x12\xc6\x24\x6e\x7b\0\0\0\x02\x09\xcf\xcd\x71\x69\xc2\x4b\xec\
\x44\x8f\x30\x58\x2e\x8c\x6d\xb9\x8d\0\0\0\x03\x13\x8c\xb7\x3e\xb4\x29\x42\x49\
\x9c\x5a\x23\x82\xb1\xdd\x0d\xc0\x93\0\0\0\x03\x16\x3f\x54\xfb\x1a\xf2\xe2\x1f\
\xea\x41\x0f\x14\xeb\x18\xfa\x76\x9e\0\0\0\x03\xbf\x9f\xbc\x0e\x8f\x60\x92\x7f\
\xef\x9d\x89\x17\x53\x53\x75\xa6\x04\0\0\x09\x02\0\0\0\0\0\0\0\0\x03\x31\x01\
\x05\x27\x0a\x21\x05\x23\x21\x05\x0c\x22\x05\x07\x06\x2e\x05\x1c\x06\x03\x63\
\x20\x05\x0e\x06\x20\x05\x07\x06\x21\x06\x3c\x05\x1c\x06\x1f\x05\x0e\x06\x2e\
\x05\x15\x2e\x05\x1a\x20\x05\x05\x06\x03\x0a\x20\x05\x09\x5a\x05\x0e\x06\x2e\
\x05\x09\x3c\x05\x0b\x06\x21\x05\x0e\x23\x05\x12\x06\x3c\x05\x0b\x06\x2f\x06\
\x03\x56\x20\x05\x09\x06\x03\x3c\x20\x05\0\x06\x03\x44\x2e\x05\x12\x06\x03\x3d\
\x20\x05\x07\x3d\x05\x0c\x21\x05\x05\x4c\x06\x03\xbf\x7f\x58\x05\x01\x06\x03\
\xc4\0\x20\x02\x01\0\x01\x01\x2f\x68\x6f\x6d\x65\x2f\x76\x6c\x61\x64\x69\x6d\
\x69\x72\x6f\x2f\x62\x61\x74\x63\x68\x69\x6e\x67\x2d\x74\x6f\x6f\x6c\x6b\x69\
\x74\x2f\x63\x6e\x74\x5f\x70\x6b\x74\0\x2f\x75\x73\x72\x2f\x69\x6e\x63\x6c\x75\
\x64\x65\x2f\x61\x73\x6d\x2d\x67\x65\x6e\x65\x72\x69\x63\0\x2f\x75\x73\x72\x2f\
\x69\x6e\x63\x6c\x75\x64\x65\x2f\x62\x70\x66\0\x2f\x75\x73\x72\x2f\x69\x6e\x63\
\x6c\x75\x64\x65\x2f\x6c\x69\x6e\x75\x78\0\x63\x6e\x74\x2e\x62\x70\x66\x2e\x63\
\0\x69\x6e\x74\x2d\x6c\x6c\x36\x34\x2e\x68\0\x62\x70\x66\x5f\x68\x65\x6c\x70\
\x65\x72\x5f\x64\x65\x66\x73\x2e\x68\0\x62\x70\x66\x2e\x68\0\x69\x66\x5f\x65\
\x74\x68\x65\x72\x2e\x68\0\x74\x79\x70\x65\x73\x2e\x68\0\0\0\0\0\0\0\0\0\0\0\0\
\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\xfe\0\0\0\x04\0\xf1\xff\0\0\0\0\0\0\0\
\0\0\0\0\0\0\0\0\0\0\0\0\0\x03\0\x03\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x45\x01\
\0\0\0\0\x03\0\xb0\x01\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x37\x01\0\0\0\0\x03\0\x20\
\x01\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x36\0\0\0\x01\0\x06\0\x1a\0\0\0\0\0\0\0\x08\0\
\0\0\0\0\0\0\x01\0\0\0\x01\0\x08\0\0\0\0\0\0\0\0\0\x08\0\0\0\0\0\0\0\x3e\x01\0\
\0\0\0\x03\0\xf0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\xc2\0\0\0\x01\0\x08\0\x08\0\0\0\
\0\0\0\0\x08\0\0\0\0\0\0\0\x30\x01\0\0\0\0\x03\0\x80\x01\0\0\0\0\0\0\0\0\0\0\0\
\0\0\0\x29\x01\0\0\0\0\x03\0\xa8\x01\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x2a\0\0\0\x01\
\0\x06\0\0\0\0\0\0\0\0\0\x1a\0\0\0\0\0\0\0\0\0\0\0\x03\0\x06\0\0\0\0\0\0\0\0\0\
\0\0\0\0\0\0\0\0\0\0\0\0\x03\0\x08\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\
\x03\0\x09\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x03\0\x0a\0\0\0\0\0\0\0\0\
\0\0\0\0\0\0\0\0\0\0\0\0\0\x03\0\x0d\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\
\x03\0\x0f\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x03\0\x10\0\0\0\0\0\0\0\0\
\0\0\0\0\0\0\0\0\0\0\0\0\0\x03\0\x16\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\
\x03\0\x18\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x03\0\x1a\0\0\0\0\0\0\0\0\
\0\0\0\0\0\0\0\0\0\x26\0\0\0\x12\0\x03\0\0\0\0\0\0\0\0\0\xb8\x01\0\0\0\0\0\0\
\x92\0\0\0\x11\0\x05\0\0\0\0\0\0\0\0\0\x20\0\0\0\0\0\0\0\xd4\0\0\0\x11\0\x07\0\
\0\0\0\0\0\0\0\0\x04\0\0\0\0\0\0\0\x90\0\0\0\0\0\0\0\x01\0\0\0\x0c\0\0\0\xc8\0\
\0\0\0\0\0\0\x01\0\0\0\x0d\0\0\0\xf0\0\0\0\0\0\0\0\x01\0\0\0\x0d\0\0\0\x40\x01\
\0\0\0\0\0\0\x01\0\0\0\x17\0\0\0\x88\x01\0\0\0\0\0\0\x01\0\0\0\x0c\0\0\0\x08\0\
\0\0\0\0\0\0\x03\0\0\0\x0f\0\0\0\x11\0\0\0\0\0\0\0\x03\0\0\0\x10\0\0\0\x15\0\0\
\0\0\0\0\0\x03\0\0\0\x14\0\0\0\x1f\0\0\0\0\0\0\0\x03\0\0\0\x12\0\0\0\x23\0\0\0\
\0\0\0\0\x03\0\0\0\x0e\0\0\0\x08\0\0\0\0\0\0\0\x03\0\0\0\x11\0\0\0\x0c\0\0\0\0\
\0\0\0\x03\0\0\0\x11\0\0\0\x10\0\0\0\0\0\0\0\x03\0\0\0\x11\0\0\0\x14\0\0\0\0\0\
\0\0\x03\0\0\0\x11\0\0\0\x18\0\0\0\0\0\0\0\x03\0\0\0\x11\0\0\0\x1c\0\0\0\0\0\0\
\0\x03\0\0\0\x11\0\0\0\x20\0\0\0\0\0\0\0\x03\0\0\0\x11\0\0\0\x24\0\0\0\0\0\0\0\
\x03\0\0\0\x11\0\0\0\x28\0\0\0\0\0\0\0\x03\0\0\0\x11\0\0\0\x2c\0\0\0\0\0\0\0\
\x03\0\0\0\x11\0\0\0\x30\0\0\0\0\0\0\0\x03\0\0\0\x11\0\0\0\x34\0\0\0\0\0\0\0\
\x03\0\0\0\x11\0\0\0\x38\0\0\0\0\0\0\0\x03\0\0\0\x11\0\0\0\x3c\0\0\0\0\0\0\0\
\x03\0\0\0\x11\0\0\0\x40\0\0\0\0\0\0\0\x03\0\0\0\x11\0\0\0\x44\0\0\0\0\0\0\0\
\x03\0\0\0\x11\0\0\0\x48\0\0\0\0\0\0\0\x03\0\0\0\x11\0\0\0\x4c\0\0\0\0\0\0\0\
\x03\0\0\0\x11\0\0\0\x50\0\0\0\0\0\0\0\x03\0\0\0\x11\0\0\0\x54\0\0\0\0\0\0\0\
\x03\0\0\0\x11\0\0\0\x58\0\0\0\0\0\0\0\x03\0\0\0\x11\0\0\0\x5c\0\0\0\0\0\0\0\
\x03\0\0\0\x11\0\0\0\x60\0\0\0\0\0\0\0\x03\0\0\0\x11\0\0\0\x64\0\0\0\0\0\0\0\
\x03\0\0\0\x11\0\0\0\x68\0\0\0\0\0\0\0\x03\0\0\0\x11\0\0\0\x6c\0\0\0\0\0\0\0\
\x03\0\0\0\x11\0\0\0\x70\0\0\0\0\0\0\0\x03\0\0\0\x11\0\0\0\x74\0\0\0\0\0\0\0\
\x03\0\0\0\x11\0\0\0\x78\0\0\0\0\0\0\0\x03\0\0\0\x11\0\0\0\x7c\0\0\0\0\0\0\0\
\x03\0\0\0\x11\0\0\0\x80\0\0\0\0\0\0\0\x03\0\0\0\x11\0\0\0\x84\0\0\0\0\0\0\0\
\x03\0\0\0\x11\0\0\0\x88\0\0\0\0\0\0\0\x03\0\0\0\x11\0\0\0\x8c\0\0\0\0\0\0\0\
\x03\0\0\0\x11\0\0\0\x90\0\0\0\0\0\0\0\x03\0\0\0\x11\0\0\0\x94\0\0\0\0\0\0\0\
\x03\0\0\0\x11\0\0\0\x98\0\0\0\0\0\0\0\x03\0\0\0\x11\0\0\0\x9c\0\0\0\0\0\0\0\
\x03\0\0\0\x11\0\0\0\xa0\0\0\0\0\0\0\0\x03\0\0\0\x11\0\0\0\xa4\0\0\0\0\0\0\0\
\x03\0\0\0\x11\0\0\0\xa8\0\0\0\0\0\0\0\x03\0\0\0\x11\0\0\0\xac\0\0\0\0\0\0\0\
\x03\0\0\0\x11\0\0\0\xb0\0\0\0\0\0\0\0\x03\0\0\0\x11\0\0\0\xb4\0\0\0\0\0\0\0\
\x03\0\0\0\x11\0\0\0\xb8\0\0\0\0\0\0\0\x03\0\0\0\x11\0\0\0\xbc\0\0\0\0\0\0\0\
\x03\0\0\0\x11\0\0\0\xc0\0\0\0\0\0\0\0\x03\0\0\0\x11\0\0\0\xc4\0\0\0\0\0\0\0\
\x03\0\0\0\x11\0\0\0\xc8\0\0\0\0\0\0\0\x03\0\0\0\x11\0\0\0\xcc\0\0\0\0\0\0\0\
\x03\0\0\0\x11\0\0\0\xd0\0\0\0\0\0\0\0\x03\0\0\0\x11\0\0\0\xd4\0\0\0\0\0\0\0\
\x03\0\0\0\x11\0\0\0\x08\0\0\0\0\0\0\0\x02\0\0\0\x0c\0\0\0\x10\0\0\0\0\0\0\0\
\x02\0\0\0\x18\0\0\0\x18\0\0\0\0\0\0\0\x02\0\0\0\x17\0\0\0\x20\0\0\0\0\0\0\0\
\x02\0\0\0\x0c\0\0\0\x28\0\0\0\0\0\0\0\x02\0\0\0\x0d\0\0\0\x30\0\0\0\0\0\0\0\
\x02\0\0\0\x0d\0\0\0\x38\0\0\0\0\0\0\0\x02\0\0\0\x02\0\0\0\x40\0\0\0\0\0\0\0\
\x02\0\0\0\x02\0\0\0\x60\x02\0\0\0\0\0\0\x04\0\0\0\x0d\0\0\0\x6c\x02\0\0\0\0\0\
\0\x04\0\0\0\x0d\0\0\0\x84\x02\0\0\0\0\0\0\x04\0\0\0\x17\0\0\0\x9c\x02\0\0\0\0\
\0\0\x03\0\0\0\x0c\0\0\0\xa8\x02\0\0\0\0\0\0\x03\0\0\0\x0c\0\0\0\xc0\x02\0\0\0\
\0\0\0\x04\0\0\0\x18\0\0\0\x2c\0\0\0\0\0\0\0\x04\0\0\0\x02\0\0\0\x40\0\0\0\0\0\
\0\0\x04\0\0\0\x02\0\0\0\x50\0\0\0\0\0\0\0\x04\0\0\0\x02\0\0\0\x60\0\0\0\0\0\0\
\0\x04\0\0\0\x02\0\0\0\x70\0\0\0\0\0\0\0\x04\0\0\0\x02\0\0\0\x80\0\0\0\0\0\0\0\
\x04\0\0\0\x02\0\0\0\x90\0\0\0\0\0\0\0\x04\0\0\0\x02\0\0\0\xa0\0\0\0\0\0\0\0\
\x04\0\0\0\x02\0\0\0\xb0\0\0\0\0\0\0\0\x04\0\0\0\x02\0\0\0\xc0\0\0\0\0\0\0\0\
\x04\0\0\0\x02\0\0\0\xd0\0\0\0\0\0\0\0\x04\0\0\0\x02\0\0\0\xe0\0\0\0\0\0\0\0\
\x04\0\0\0\x02\0\0\0\xf0\0\0\0\0\0\0\0\x04\0\0\0\x02\0\0\0\0\x01\0\0\0\0\0\0\
\x04\0\0\0\x02\0\0\0\x10\x01\0\0\0\0\0\0\x04\0\0\0\x02\0\0\0\x20\x01\0\0\0\0\0\
\0\x04\0\0\0\x02\0\0\0\x30\x01\0\0\0\0\0\0\x04\0\0\0\x02\0\0\0\x40\x01\0\0\0\0\
\0\0\x04\0\0\0\x02\0\0\0\x50\x01\0\0\0\0\0\0\x04\0\0\0\x02\0\0\0\x60\x01\0\0\0\
\0\0\0\x04\0\0\0\x02\0\0\0\x70\x01\0\0\0\0\0\0\x04\0\0\0\x02\0\0\0\x80\x01\0\0\
\0\0\0\0\x04\0\0\0\x02\0\0\0\x90\x01\0\0\0\0\0\0\x04\0\0\0\x02\0\0\0\xa0\x01\0\
\0\0\0\0\0\x04\0\0\0\x02\0\0\0\xb0\x01\0\0\0\0\0\0\x04\0\0\0\x02\0\0\0\xc0\x01\
\0\0\0\0\0\0\x04\0\0\0\x02\0\0\0\xd0\x01\0\0\0\0\0\0\x04\0\0\0\x02\0\0\0\xe0\
\x01\0\0\0\0\0\0\x04\0\0\0\x02\0\0\0\xf0\x01\0\0\0\0\0\0\x04\0\0\0\x02\0\0\0\
\x14\0\0\0\0\0\0\0\x03\0\0\0\x13\0\0\0\x18\0\0\0\0\0\0\0\x02\0\0\0\x02\0\0\0\
\x22\0\0\0\0\0\0\0\x03\0\0\0\x15\0\0\0\x26\0\0\0\0\0\0\0\x03\0\0\0\x15\0\0\0\
\x2a\0\0\0\0\0\0\0\x03\0\0\0\x15\0\0\0\x2e\0\0\0\0\0\0\0\x03\0\0\0\x15\0\0\0\
\x3a\0\0\0\0\0\0\0\x03\0\0\0\x15\0\0\0\x4f\0\0\0\0\0\0\0\x03\0\0\0\x15\0\0\0\
\x64\0\0\0\0\0\0\0\x03\0\0\0\x15\0\0\0\x79\0\0\0\0\0\0\0\x03\0\0\0\x15\0\0\0\
\x8e\0\0\0\0\0\0\0\x03\0\0\0\x15\0\0\0\xa3\0\0\0\0\0\0\0\x03\0\0\0\x15\0\0\0\
\xbd\0\0\0\0\0\0\0\x02\0\0\0\x02\0\0\0\x16\x17\x0b\x18\x05\0\x6d\x61\x78\0\x2e\
\x64\x65\x62\x75\x67\x5f\x61\x62\x62\x72\x65\x76\0\x2e\x74\x65\x78\x74\0\x2e\
\x72\x65\x6c\x2e\x42\x54\x46\x2e\x65\x78\x74\0\x63\x6e\x74\0\x63\x6e\x74\x2e\
\x5f\x5f\x5f\x5f\x66\x6d\x74\0\x67\x65\x74\x5f\x69\x64\x2e\x5f\x5f\x5f\x5f\x66\
\x6d\x74\0\x2e\x64\x65\x62\x75\x67\x5f\x6c\x6f\x63\x6c\x69\x73\x74\x73\0\x2e\
\x72\x65\x6c\x2e\x64\x65\x62\x75\x67\x5f\x73\x74\x72\x5f\x6f\x66\x66\x73\x65\
\x74\x73\0\x2e\x62\x73\x73\0\x2e\x6d\x61\x70\x73\0\x2e\x64\x65\x62\x75\x67\x5f\
\x73\x74\x72\0\x2e\x64\x65\x62\x75\x67\x5f\x6c\x69\x6e\x65\x5f\x73\x74\x72\0\
\x63\x6f\x75\x6e\x74\x65\x72\0\x2e\x72\x65\x6c\x2e\x64\x65\x62\x75\x67\x5f\x61\
\x64\x64\x72\0\x2e\x72\x65\x6c\x78\x64\x70\0\x2e\x72\x65\x6c\x2e\x64\x65\x62\
\x75\x67\x5f\x69\x6e\x66\x6f\0\x6d\x69\x6e\0\x2e\x6c\x6c\x76\x6d\x5f\x61\x64\
\x64\x72\x73\x69\x67\0\x5f\x6c\x69\x63\x65\x6e\x73\x65\0\x2e\x72\x65\x6c\x2e\
\x64\x65\x62\x75\x67\x5f\x6c\x69\x6e\x65\0\x2e\x72\x65\x6c\x2e\x64\x65\x62\x75\
\x67\x5f\x66\x72\x61\x6d\x65\0\x63\x6e\x74\x2e\x62\x70\x66\x2e\x63\0\x2e\x73\
\x74\x72\x74\x61\x62\0\x2e\x73\x79\x6d\x74\x61\x62\0\x2e\x72\x6f\x64\x61\x74\
\x61\0\x2e\x72\x65\x6c\x2e\x42\x54\x46\0\x4c\x42\x42\x30\x5f\x39\0\x4c\x42\x42\
\x30\x5f\x38\0\x4c\x42\x42\x30\x5f\x36\0\x4c\x42\x42\x30\x5f\x34\0\x4c\x42\x42\
\x30\x5f\x31\x30\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\
\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\
\0\x08\x01\0\0\x03\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x3d\x1e\0\0\0\0\0\0\
\x4d\x01\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x01\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x13\0\0\
\0\x01\0\0\0\x06\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x40\0\0\0\0\0\0\0\0\0\0\0\0\0\0\
\0\0\0\0\0\0\0\0\0\x04\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\xae\0\0\0\x01\0\0\0\x06\0\
\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x40\0\0\0\0\0\0\0\xb8\x01\0\0\0\0\0\0\0\0\0\0\0\0\
\0\0\x08\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\xaa\0\0\0\x09\0\0\0\x40\0\0\0\0\0\0\0\0\
\0\0\0\0\0\0\0\xd8\x16\0\0\0\0\0\0\x50\0\0\0\0\0\0\0\x1c\0\0\0\x03\0\0\0\x08\0\
\0\0\0\0\0\0\x10\0\0\0\0\0\0\0\x71\0\0\0\x01\0\0\0\x03\0\0\0\0\0\0\0\0\0\0\0\0\
\0\0\0\xf8\x01\0\0\0\0\0\0\x20\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x08\0\0\0\0\0\0\0\
\0\0\0\0\0\0\0\0\x18\x01\0\0\x01\0\0\0\x02\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x18\
\x02\0\0\0\0\0\0\x22\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x01\0\0\0\0\0\0\0\0\0\0\0\0\
\0\0\0\xd5\0\0\0\x01\0\0\0\x03\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x3a\x02\0\0\0\0\0\
\0\x04\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x01\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x6c\0\0\
\0\x08\0\0\0\x03\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x40\x02\0\0\0\0\0\0\x10\0\0\0\0\
\0\0\0\0\0\0\0\0\0\0\0\x08\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x45\0\0\0\x01\0\0\0\0\
\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x40\x02\0\0\0\0\0\0\x73\0\0\0\0\0\0\0\0\0\0\0\0\
\0\0\0\x01\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x05\0\0\0\x01\0\0\0\0\0\0\0\0\0\0\0\0\
\0\0\0\0\0\0\0\xb3\x02\0\0\0\0\0\0\x9f\x01\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x01\0\0\
\0\0\0\0\0\0\0\0\0\0\0\0\0\xb6\0\0\0\x01\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\
\x52\x04\0\0\0\0\0\0\xb4\x02\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x01\0\0\0\0\0\0\0\0\0\
\0\0\0\0\0\0\xb2\0\0\0\x09\0\0\0\x40\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x28\x17\0\0\
\0\0\0\0\x50\0\0\0\0\0\0\0\x1c\0\0\0\x0b\0\0\0\x08\0\0\0\0\0\0\0\x10\0\0\0\0\0\
\0\0\x59\0\0\0\x01\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x06\x07\0\0\0\0\0\0\
\xd8\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x01\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x55\0\0\0\
\x09\0\0\0\x40\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x78\x17\0\0\0\0\0\0\x40\x03\0\0\0\
\0\0\0\x1c\0\0\0\x0d\0\0\0\x08\0\0\0\0\0\0\0\x10\0\0\0\0\0\0\0\x77\0\0\0\x01\0\
\0\0\x30\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\xde\x07\0\0\0\0\0\0\x30\x02\0\0\0\0\0\0\
\0\0\0\0\0\0\0\0\x01\0\0\0\0\0\0\0\x01\0\0\0\0\0\0\0\x9e\0\0\0\x01\0\0\0\0\0\0\
\0\0\0\0\0\0\0\0\0\0\0\0\0\x0e\x0a\0\0\0\0\0\0\x48\0\0\0\0\0\0\0\0\0\0\0\0\0\0\
\0\x01\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x9a\0\0\0\x09\0\0\0\x40\0\0\0\0\0\0\0\0\0\
\0\0\0\0\0\0\xb8\x1a\0\0\0\0\0\0\x80\0\0\0\0\0\0\0\x1c\0\0\0\x10\0\0\0\x08\0\0\
\0\0\0\0\0\x10\0\0\0\0\0\0\0\x24\x01\0\0\x01\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\
\0\0\x58\x0a\0\0\0\0\0\0\x0b\x06\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x04\0\0\0\0\0\0\0\
\0\0\0\0\0\0\0\0\x20\x01\0\0\x09\0\0\0\x40\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x38\
\x1b\0\0\0\0\0\0\x60\0\0\0\0\0\0\0\x1c\0\0\0\x12\0\0\0\x08\0\0\0\0\0\0\0\x10\0\
\0\0\0\0\0\0\x1d\0\0\0\x01\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x64\x10\0\0\0\
\0\0\0\0\x02\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x04\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x19\
\0\0\0\x09\0\0\0\x40\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x98\x1b\0\0\0\0\0\0\xd0\x01\
\0\0\0\0\0\0\x1c\0\0\0\x14\0\0\0\x08\0\0\0\0\0\0\0\x10\0\0\0\0\0\0\0\xf1\0\0\0\
\x01\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x68\x12\0\0\0\0\0\0\x28\0\0\0\0\0\0\
\0\0\0\0\0\0\0\0\0\x08\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\xed\0\0\0\x09\0\0\0\x40\0\
\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x68\x1d\0\0\0\0\0\0\x20\0\0\0\0\0\0\0\x1c\0\0\0\
\x16\0\0\0\x08\0\0\0\0\0\0\0\x10\0\0\0\0\0\0\0\xe1\0\0\0\x01\0\0\0\0\0\0\0\0\0\
\0\0\0\0\0\0\0\0\0\0\x90\x12\0\0\0\0\0\0\x43\x01\0\0\0\0\0\0\0\0\0\0\0\0\0\0\
\x01\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\xdd\0\0\0\x09\0\0\0\x40\0\0\0\0\0\0\0\0\0\0\
\0\0\0\0\0\x88\x1d\0\0\0\0\0\0\xb0\0\0\0\0\0\0\0\x1c\0\0\0\x18\0\0\0\x08\0\0\0\
\0\0\0\0\x10\0\0\0\0\0\0\0\x82\0\0\0\x01\0\0\0\x30\0\0\0\0\0\0\0\0\0\0\0\0\0\0\
\0\xd3\x13\0\0\0\0\0\0\xa6\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x01\0\0\0\0\0\0\0\x01\
\0\0\0\0\0\0\0\xc6\0\0\0\x03\x4c\xff\x6f\0\0\0\x80\0\0\0\0\0\0\0\0\0\0\0\0\x38\
\x1e\0\0\0\0\0\0\x05\0\0\0\0\0\0\0\x1c\0\0\0\0\0\0\0\x01\0\0\0\0\0\0\0\0\0\0\0\
\0\0\0\0\x10\x01\0\0\x02\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\x80\x14\0\0\0\0\
\0\0\x58\x02\0\0\0\0\0\0\x01\0\0\0\x16\0\0\0\x08\0\0\0\0\0\0\0\x18\0\0\0\0\0\0\
\0";

	*sz = sizeof(data) - 1;
	return (const void *)data;
}

#ifdef __cplusplus
struct cnt_bpf *cnt_bpf::open(const struct bpf_object_open_opts *opts) { return cnt_bpf__open_opts(opts); }
struct cnt_bpf *cnt_bpf::open_and_load() { return cnt_bpf__open_and_load(); }
int cnt_bpf::load(struct cnt_bpf *skel) { return cnt_bpf__load(skel); }
int cnt_bpf::attach(struct cnt_bpf *skel) { return cnt_bpf__attach(skel); }
void cnt_bpf::detach(struct cnt_bpf *skel) { cnt_bpf__detach(skel); }
void cnt_bpf::destroy(struct cnt_bpf *skel) { cnt_bpf__destroy(skel); }
const void *cnt_bpf::elf_bytes(size_t *sz) { return cnt_bpf__elf_bytes(sz); }
#endif /* __cplusplus */

__attribute__((unused)) static void
cnt_bpf__assert(struct cnt_bpf *s __attribute__((unused)))
{
#ifdef __cplusplus
#define _Static_assert static_assert
#endif
#ifdef __cplusplus
#undef _Static_assert
#endif
}

#endif /* __CNT_BPF_SKEL_H__ */
