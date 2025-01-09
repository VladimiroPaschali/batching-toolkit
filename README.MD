# Batching-Toolkit

## PCAP generation

This repository contains a Python-based tool for generating network packet traces. The tool creates packets with various configurations, including different protocols, distributions, and flow characteristics. The generated packets can be saved in `.pcap` format for further analysis.

This can be done using one og the following files:

- [traccia.py](traccia.py) That generates regular packets
- [tracciaBatch.py](tracciaBatch.py) That generates batched packets

### traccia.py

Install dependencies using:
```bash
pip install scapy numpy tqdm
```

### Usage
Run the script from the command line:
```bash
python traccia.py [OPTIONS]
```

### Command-Line Arguments
| Argument            | Description                                                                                                  | Default       |
|---------------------|--------------------------------------------------------------------------------------------------------------|---------------|
| `--n_pkts`         | Number of packets to generate. Supports shorthand (e.g., `1K`, `1M`).                                      | 100           |
| `--n_flows`        | Number of flows to generate. Supports shorthand (e.g., `1K`, `1M`).                                         | 40            |
| `--l4_proto`       | Layer 4 protocol to use (`TCP`, `UDP`, or `MIX`).                                                           | `UDP`         |
| `--locality_size`  | Parameter for selecting close packets or the number of packets per queue.                                   | 2             |
| `--distribution`   | Distribution type (`ZIPF`, `UNIFORM`, or `LOCALITY`).                                                       | `UNIFORM`     |
| `--output`         | Output file name prefix.                                                                                    | Empty string  |
| `--payload_size`   | Average payload size in bytes, calculated using a Gaussian distribution (std. dev. = 2).                   | 10            |
| `--s_subnet`       | Source IP subnet.                                                                                           | `0.0.0.0/0`   |
| `--d_subnet`       | Destination IP subnet.                                                                                      | `0.0.0.0/0`   |
| `--n_queues`       | Number of queues for hash-based packet assignment.                                                          | 2             |


### Examples
1. Generate 1,000 packets with 50 flows using TCP protocol:
   ```bash
   python traccia.py --n_pkts 1K --n_flows 50 --l4_proto TCP
   ```

2. Generate packets with a Zipf distribution and a payload size of 20 bytes:
   ```bash
   python traccia.py --n_pkts 1M --n_flows 100K --distribution ZIPF --payload_size 20
   ```

3. Generate packets ordering them by flows 10 at a time:
   ```bash
   python traccia.py --n_pkts 1M --n_flows 100K --distribution LOCALITY --locality-size 10
   ```

4. Generates 100K flows uniformly distributed among 1M pkts and another pcap trace with packets reordered simulating RSS with 256 queues
    ```bash
   python traccia.py --n_pkts 1M --n_flows 100K --distribution UNIFORM --n_queues 1K --locality_size 1K
   ```


### tracciaBatch.py

This tool generates network packets and organizes them into batches with a custom `batching` header.

Install dependencies using:
```bash
pip install scapy numpy tqdm
```

### Usage
Run the script from the command line:
```bash
python tracciaBatch.py [OPTIONS]
```
### Command-Line Arguments

| Argument              | Description                                                                 | Default            |
|-----------------------|-----------------------------------------------------------------------------|--------------------|
| `--n_pkts`           | Number of packets to generate. Supports shorthand (e.g., `1K`, `1M`).        | `10`              |
| `--n_flows`          | Number of flows to generate Supports shorthand (e.g., `1K`, `1M`).          | `4`               |
| `--l4_proto`         | Layer 4 protocol: `TCP`, `UDP`, or `MIX`.                                  | `UDP`             |
| `--dist_param`       | Distribution parameter for Zipf or locality.                              | `2`               |
| `--distribution`     | Packet distribution type: `ZIPF`, `UNIFORM`, `LOCALITY`, `RSS`.            | `ZIPF`            |
| `--output`           | Name of the output `.pcap` file.                                           | `batch`           |
| `--batch_size`       | Number of packets per batch.                                               | `2`               |
| `--avg_payload_size` | Average payload size (Gaussian distribution).                             | `10`              |
| `--payload_size`     | Fixed payload size for each packet.                                        | `0`               |
| `--pkt_size`         | Total packet size (must be >= minimum size).                              | `0`               |
| `--total_batch_size` | Total batch size (must be >= minimum size).                               | `0`               |
| `--s_subnet`         | Source subnet IP range.                                                    | `0.0.0.0/0`       |
| `--d_subnet`         | Destination subnet IP range.                                               | `0.0.0.0/0`       |
| `--fixed`            | Use fixed source/destination MAC and ports.                               | `False`           |
| `--multicore`        | Modify destination MAC to simulate multicore environments.                | `False`           |
| `--n_queues`         | Number of queues for RSS distribution.                                    | `2`               |
| `--locality_size`    | Number of packets chosen per queue in locality distribution.              | `2`               |

### Examples

1. Generate 1000 packets batched 2 at a time distributed uniformly across 10 flows:

```bash
python tracciaBatch.py --batch_size 2 --n_pkts 1K --n_flows 10 --distribution UNIFORM
```

2. Generates 1M pks with 100K flows batched 4 at a time and reordered simulating RSS with 256 queues

```bash
python tracciaBatch.py --n_pkts 1M --n_flows 100K --batch_size 4 --distribution RSS --n_queues 256 --locality_size 256
```


## Testing Suite

## Config

Create a `config.json` file in the `ez-test/suites/testname` folder


| **Key**             | **Description**                                                                                                                                          | **Example Value**                               |
|---------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------|
| **`ifname`**        | The name of the network interface to be used.                                                                                                            | `enp52s0f1np1`                                          |
| **`exp-dir`**       | Directory where experiment data is stored.                                                                                                               | `/home/vladimiro/bxdp`                                  |
| **`ioctl-dir`**     | Directory containing IOCTL utilities.                                                                                                                    | `/home/andrea/mellanox_batching/utils`                  |
| **`time`**          | Duration of each experiment in seconds.                                                                                                                  | `10`                                                   |
| **`repetitions`**   | Number of repetitions for the experiment.                                                                                                                | `1`                                                    |
| **`progs`**         | List of programs to execute. Each program includes a `name`, `path`, and optionally `args`.                                                             | See below for details.                                  |
| **`before_start`**  | List of pre-execution commands to validate the environment. Each command includes a `name`, `cmd`, and expected `output`.                               | See below for details.                                  |
| **`batched`**       | Whether batched execution is enabled (`true` or `false`).                                                                                                | `true`                                                 |
| **`bpf-stats`**     | Enable or disable BPF statistics (`true` or `false`).                                                                                                    | `false`                                                |
| **`throughput`**    | Enable or disable throughput measurement (`true` or `false`).                                                                                            | `true`                                                 |
| **`bandwidth`**     | Enable or disable bandwidth measurement (`true` or `false`).                                                                                             | `false`                                                |
| **`cpu`**           | CPU core to be used for the experiments.                                                                                                                 | `0`                                                    |
| **`perfIPC`**       | Enable or disable performance monitoring for instructions per cycle.                                                                                     | `true`                                                 |
| **`perfCacheMisses`** | Enable or disable performance monitoring for cache misses.                                                                                              | `true`                                                 |
| **`perfIPP`**       | Enable or disable performance monitoring for instructions per packet.                                                                                     | `true`                                                 |
| **`perfBranchMisses`** | Enable or disable performance monitoring for branch misses.                                                                                             | `false`                                                |

---

## Programs (`progs`)

| **Name**      | **Path**          | **Arguments** (Optional)   |
|---------------|-------------------|----------------------------|
| `bdrop`       | `drop/bdrop`      | -                          |
| `bpass`       | `pass/bpass`      | -                          |
| `bcms`        | `cms/bcms`        | -                          |
| `bconntrack`  | `conntrack/bconntrack` | -                          |
| `brouter`     | `router/brouter`  | -                          |
| `bnat`        | `nat/bnat`        | `@/nat/nat_tbl.txt`        |
| `btx`         | `tx/btx`          | -                          |

---

## Pre-Execution Commands (`before_start`)

| **Name**           | **Command**                                                                                               | **Expected Output**                                   |
|--------------------|---------------------------------------------------------------------------------------------------------|-----------------------------------------------------|
| `bpf_stats`        | `sysctl kernel.bpf_stats_enabled`                                                                        | `0$`                                                |
| `batched`          | `/home/andrea/mellanox_batching/utils/ioctl 6`                                                           | `1`                                                 |
| `CPU frequency`    | `cpupower -c 0 frequency-info | sed -n 's/.*current CPU frequency: \([0-9.]\+ [MG]Hz\).*/\1/p'`        | `^(2\.(9[0-9])|3\.([0-9]{2}|10)) GHz$`              |

---


## Running tests

```bash
sudo python main.py run --name testname
```