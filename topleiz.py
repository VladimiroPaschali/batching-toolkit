#!/usr/bin/env python
#-*- coding: utf-8 -*-

# Test data including the secret key, ip, port numbers and the hash values 
# as the result is from "Intel Ethernet Controller 710 Series Datasheet".

KEY=[]

def reset_key():
    global KEY
    KEY = [
        0x6d, 0x5a, 0x56, 0xda, 0x25, 0x5b, 0x0e, 0xc2,
        0x41, 0x67, 0x25, 0x3d, 0x43, 0xa3, 0x8f, 0xb0,
        0xd0, 0xca, 0x2b, 0xcb, 0xae, 0x7b, 0x30, 0xb4,
        0x77, 0xcb, 0x2d, 0xa3, 0x80, 0x30, 0xf2, 0x0c,
        0x6a, 0x42, 0xb7, 0x3b, 0xbe, 0xac, 0x01, 0xfa,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00
    ]


def left_most_32bits_of_key():
    return (KEY[0] << 24) | (KEY[1] << 16) | (KEY[2] << 8) | KEY[3]

def shift_key():
    bitstr = ''
    for k in KEY:
       bitstr += bin(k)[2:].zfill(8)
    shifted = bitstr[1:]
    shifted += bitstr[0]
    for i, k in enumerate(KEY):
        KEY[i] = int(shifted[:8], 2)
        shifted = shifted[8:]

def compute_hash(input_bytes, N):
    reset_key()
    result = 0;
    bitstr = ''
    for b in input_bytes:
        bitstr += bin(b)[2:].zfill(8) # eliminate prefix "0b" and fill zeros to fit into 8 bits
    for b in bitstr:
        if b == '1':
            result ^= left_most_32bits_of_key()
        shift_key()
    return result

def get_ip_number(ip):
    ipnum = ip.split('.')
    return int(ipnum[0]) << 24 | int(ipnum[1]) << 16 | int(ipnum[2]) << 8 | int(ipnum[3])

def get_input(srcip, dstip, srcport, dstport):
    srcip_num = get_ip_number(srcip)
    dstip_num = get_ip_number(dstip)
    input_bytes = []
    input_bytes.append((srcip_num & 0xff000000) >> 24)
    input_bytes.append((srcip_num & 0x00ff0000) >> 16)
    input_bytes.append((srcip_num & 0x0000ff00) >> 8)
    input_bytes.append(srcip_num & 0x000000ff)
    input_bytes.append((dstip_num & 0xff000000) >> 24)
    input_bytes.append((dstip_num & 0x00ff0000) >> 16)
    input_bytes.append((dstip_num & 0x0000ff00) >> 8)
    input_bytes.append(dstip_num & 0x000000ff)
    input_bytes.append((srcport & 0xff00) >> 8)
    input_bytes.append(srcport & 0x00ff)
    input_bytes.append((dstport & 0xff00) >> 8)
    input_bytes.append(dstport & 0x00ff)
    return input_bytes
