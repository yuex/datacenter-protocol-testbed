#!/usr/bin/env sh
# justdoit.sh num
# just do it for how many times

source ./justdoit.conf

for i in `seq $1 $2`;do
    #./trafficgen.sh gen $duration ipf traffic${duration}s
    ./trafficgen.sh upload ipf traffic${duration}s

	# do dctcp experiment
    ./trafficgen.sh exec ipf stopserver
	./trafficgen.sh exec ipf stopserver
    
    ./trafficgen.sh exec ipf 'sysctl -w net.ipv4.tcp_ltpb_enable=0'
	./trafficgen.sh exec ipf dctcpwrite 1

	./trafficgen.sh exec ipf startserver $backport $queryport

	./benchmarkstart.sh ipf

	echo waiting dctcp${hostnumber}s${duration}s.${switchbuffer}kbswitch.singletomany.$i
    echo `date`
	sleep $intvl

	./getlog.sh
	./striplog.sh log/dctcp${hostnumber}s${duration}s.${switchbuffer}kbswitch.singletomany.$i

	# do tcp experiment
    ./trafficgen.sh exec ipf stopserver
	./trafficgen.sh exec ipf stopserver
    
    ./trafficgen.sh exec ipf 'sysctl -w net.ipv4.tcp_ltpb_enable=0'
	./trafficgen.sh exec ipf dctcpwrite 0

	./trafficgen.sh exec ipf startserver $backport $queryport

	./benchmarkstart.sh ipf

	echo waiting tcp${hostnumber}s${duration}s.${switchbuffer}kbswitch.singletomany.$i
    echo `date`
	sleep $intvl

	./getlog.sh
	./striplog.sh log/tcp${hostnumber}s${duration}s.${switchbuffer}kbswitch.singletomany.$i

done
