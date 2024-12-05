#!/bin/bash
# if [ -d pcap ]; then
#     rm -drf pcap
# fi


# mkdir pcap
# mkdir pcap/2pkts
# mkdir pcap/2pkts/single
# ( cd pcap/2pkts/single; python ../../../tracciaBatch.py --n_pkts 2 --n_flows 1 --batch_size 2 ) &

# mkdir pcap/2pkts/1Kqueues
(cd pcap/2pkts/1Kqueues; python ../../../tracciaBatch.py --n_pkts 1M --n_flows 100K --batch_size 2 --distribution RSS --n_queues 1K --locality_size 1K) &
(cd pcap/2pkts/1Kqueues; python ../../../tracciaBatch.py --n_pkts 1M --n_flows 10K --batch_size 2 --distribution RSS --n_queues 1K --locality_size 1K) &

# mkdir pcap/2pkts/512queues
( cd pcap/2pkts/512queues; python ../../../tracciaBatch.py --n_pkts 1M --n_flows 10K --batch_size 2 --distribution RSS --n_queues 512 --locality_size 512) &

# mkdir pcap/2pkts/256queues
(cd pcap/2pkts/256queues; python ../../../tracciaBatch.py --n_pkts 1M --n_flows 10K --batch_size 2 --distribution RSS --n_queues 256 --locality_size 256) &

# mkdir pcap/2pkts/locality
# (cd pcap/2pkts/locality; python ../../../tracciaBatch.py --n_pkts 1M --n_flows 100K --batch_size 2 --distribution LOCALITY) &
# (cd pcap/2pkts/locality; python ../../../tracciaBatch.py --n_pkts 1M --n_flows 10K --batch_size 2 --distribution LOCALITY) &

# mkdir pcap/3pkts
# mkdir pcap/3pkts/single
# ( cd pcap/3pkts/single; python ../../../tracciaBatch.py --n_pkts 3 --n_flows 1 --batch_size 3 ) &

# mkdir pcap/3pkts/1Kqueues
(cd pcap/3pkts/1Kqueues; python ../../../tracciaBatch.py --n_pkts 1M --n_flows 100K --batch_size 3 --distribution RSS --n_queues 1K --locality_size 1K) &
(cd pcap/3pkts/1Kqueues; python ../../../tracciaBatch.py --n_pkts 1M --n_flows 10K --batch_size 3 --distribution RSS --n_queues 1K --locality_size 1K) &

# mkdir pcap/3pkts/512queues
( cd pcap/3pkts/512queues; python ../../../tracciaBatch.py --n_pkts 1M --n_flows 10K --batch_size 3 --distribution RSS --n_queues 512 --locality_size 512) &

# mkdir pcap/3pkts/256queues
(cd pcap/3pkts/256queues; python ../../../tracciaBatch.py --n_pkts 1M --n_flows 10K --batch_size 3 --distribution RSS --n_queues 256 --locality_size 256) &

# mkdir pcap/3pkts/locality
# (cd pcap/3pkts/locality; python ../../../tracciaBatch.py --n_pkts 1M --n_flows 100K --batch_size 3 --distribution LOCALITY) &
# (cd pcap/3pkts/locality; python ../../../tracciaBatch.py --n_pkts 1M --n_flows 10K --batch_size 3 --distribution LOCALITY) &


# mkdir pcap/4pkts
# mkdir pcap/4pkts/single
# ( cd pcap/4pkts/single; python ../../../tracciaBatch.py --n_pkts 4 --n_flows 1 --batch_size 4 ) &

# mkdir pcap/4pkts/1Kqueues
(cd pcap/4pkts/1Kqueues; python ../../../tracciaBatch.py --n_pkts 1M --n_flows 100K --batch_size 4 --distribution RSS --n_queues 1K --locality_size 1K) &
(cd pcap/4pkts/1Kqueues; python ../../../tracciaBatch.py --n_pkts 1M --n_flows 10K --batch_size 4 --distribution RSS --n_queues 1K --locality_size 1K) &

# mkdir pcap/4pkts/512queues
( cd pcap/4pkts/512queues; python ../../../tracciaBatch.py --n_pkts 1M --n_flows 10K --batch_size 4 --distribution RSS --n_queues 512 --locality_size 512) &

# mkdir pcap/4pkts/256queues
(cd pcap/4pkts/256queues; python ../../../tracciaBatch.py --n_pkts 1M --n_flows 10K --batch_size 4 --distribution RSS --n_queues 256 --locality_size 256) &

# mkdir pcap/4pkts/locality
# (cd pcap/4pkts/locality; python ../../../tracciaBatch.py --n_pkts 1M --n_flows 100K --batch_size 4 --distribution LOCALITY) &
# (cd pcap/4pkts/locality; python ../../../tracciaBatch.py --n_pkts 1M --n_flows 10K --batch_size 4 --distribution LOCALITY) &






