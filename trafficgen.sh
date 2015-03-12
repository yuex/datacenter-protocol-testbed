#!/usr/bin/env sh

USAGE="$0: USAGE $0 {gen|upload|exec|help}"

printerror(){
	echo -e "$1" >&2
	exit $2
}

if [[ $# < 1 ]];then
	printerror "$USAGE" 1
fi

MODE="$1"
shift

case "$MODE" in 
	
	ping)
		USAGE="$0: USAGE $0 ping ipf"

		if [[ $# < 1 ]]; then
			printerror "$USAGE" 2
		fi

		IPF="$1"
		for ip in `cat $IPF`;do
			echo -e "\n\t\t***** $ip *****\n"
			ping -c4 $ip
		done
		;;

	gen)
	# generate background traffic, flow size and interval are according with patterns in dctcp
		USAGE="$0: USAGE $0 gen duration ip_file [traffic_dir]"

		if [[ $# < 2 ]]; then
			printerror "$USAGE" 2
		fi

		DUR=$1
		IPF="$2"
		OUTDIR=${3:-"traffic/"}

		if [ -d "$OUTDIR" ];then
			rm -rf "$OUTDIR"
		fi
		mkdir $OUTDIR

		for ip in `cat $IPF`;
		do
			python queryintvl.py $1 $IPF $ip >$OUTDIR/$ip.query
			#python backintvl.py $1 $IPF $ip >$OUTDIR/$ip.back
			for dip in `cat $IPF`;
			do 
				if [[ $ip != $dip ]];then
					python backintvl.py $1 $IPF $dip >$OUTDIR/$ip.$dip.back
				fi
			done
		done

		;;
	
	upload)
	# upload the traffic generated in gen) to hosts, specified in ip_file
		USAGE="$0: USAGE $0 upload ip_file [traffic_dir]"

		if [[ $# < 1 ]]; then
			printerror "$USAGE" 2
		fi

		IPF="$1"
		TRAFFIC_DIR=${2:-"traffic"}
		UPLOAD_DIR="sab/misc"
		if [ ! -d "$TRAFFIC_DIR" ]; then
			printerror "$USAGE" 3
		fi

		echo $UPLOAD_DIR
		echo $TRAFFIC_DIR

		for ip in `cat $IPF`; do
			ssh $ip "cd $UPLOAD_DIR; rm *.{query,back,stdout,stderr}"
			scp "$TRAFFIC_DIR/$ip.query" $ip:"$UPLOAD_DIR"
			#scp "$TRAFFIC_DIR/$ip.back" $ip:"$UPLOAD_DIR"
			for dip in `cat $IPF`;do
				if [[ $ip != $dip ]];then
					scp "$TRAFFIC_DIR/$ip.$dip.back" $ip:"$UPLOAD_DIR"
				fi
			done
		done

		;;

	exec)
	# ssh to each server specified in ip_file, exec command. for convinience, some frequently used commands are specified, see inner case
		USAGE="$0: USAGE $0 exec ip_file command"

		if [[ $# < 2 ]]; then
			printerror "$USAGE" 2
		fi

		IPF="$1"
		COMM="$2"

		shift;shift

		case "$COMM" in
			startserver)
			# ssh to each server, start the server daemon. (thdserver.py)
			# there are dirty hacks. be ***CAUTIOUS*** when modifying this block
				USAGE="$0: USAGE $MODE $IPF startserver backport queryport"
				if [[ $# < 1 ]]; then
					printerror "$USAGE" 2
				fi

				BACKPORT="$1"
                QUERYPORT="$2"

				DIR="sab/misc"
				WARNING="!! IMPORTANT !!\n
				run stopserver first\n
				cd $DIR on remote server! BE CAREFULL !!\n
				!! fd >ip.stdout 2>ip.stderr\n"

				echo -e $WARNING >&2
				for ip in `cat $IPF`; do
					ssh $ip "cd $DIR; python thdserver.py $BACKPORT >$ip.back.recv.stdout 2>$ip.back.recv.stderr &"
                    ssh $ip "cd $DIR; python thdserver.py $QUERYPORT >$ip.query.recv.stdout 2>$ip.query.recv.stderr &"
					echo $ip
				done
				;;
			stopserver)
			# send KeyboardInterrupt to server daemon. for convinience, just implemented as killall -2 python
				USAGE="$0: USAGE $MODE $IPF stopserver"

				WARNING="!! IMPORTANT\n
				killall -9 python will be send to each server\n
				run stopserver again to verify\n"
				echo -e $WARNING >&2

				for ip in `cat $IPF`; do
					echo $ip
					ssh $ip "killall -9 python"
				done
				;;
			grep)
			# ps -ef | grep string. grep process itself not included
				USAGE="$0: USAGE $MODE $IPF grep string"
				if [[ $# < 1 ]]; then
					printerror "$USAGE" 2
				fi

				STR="$1"

				for ip in `cat $IPF`; do
					echo "*** $ip ***"
					ssh $ip "ps -ef|grep -v grep|grep $STR || echo null"
				done
				;;
			dctcpwrite)
				USAGE="$0: USAGE $MODE $IPF dctcpwrite 1|0"
				if [[ $# < 1 ]]; then
					printerror "$USAGE" 2
				fi

				FLAG="$1"
				for ip in `cat $IPF`; do
					echo $ip
					ssh $ip "sysctl -w net.ipv4.tcp_dctcp_enable=$FLAG"
				done
				;;
			ltpbwrite)
				USAGE="$0: USAGE $MODE $IPF ltpbwrite 1|0"
				if [[ $# < 1 ]]; then
					printerror "$USAGE" 2
				fi

				FLAG="$1"
				for ip in `cat $IPF`; do
					echo $ip
					ssh $ip "sysctl -w net.ipv4.tcp_ltpb_enable=$FLAG"
				done
				;;
			*)
			# other commands
				for ip in `cat $IPF`; do
					echo $ip
					ssh $ip "$COMM"
				done
				;;
		esac

		;;
	
	help)
		USAGE="$0 help
gen	generate background traffic scripts, named with ip, 
	stored in traffic_dir
upload	upload traffic scripts in traffic_dir to host, according to the 
	file name ( must be the ip addr of the host)
exec	loop through the ip_file, ssh to the host and execute the command
help	print these
"

		printerror "$USAGE" 0
		;;
	
	*)
		printerror "$USAGE" 1
		;;

esac
