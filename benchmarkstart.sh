#!/usr/bin/env sh
USAGE="usage ip_file"
if [[ $# < 1 ]]; then
	echo $USAGE >&2
	exit
fi

IPF="$1"
QRY="$2"
MYIP="$3"
DIR="sab/misc"

#echo 'starting BACK sending' `date +%s.%N`
for ip in `cat $IPF`;do
	echo "ssh to $ip..."

	ssh $ip '(cd sab/misc
	for intvlfile in `ls *.back`;do
		(python pysend.py back $intvlfile >$intvlfile.send.stdout 2>$intvlfile.send.stderr &)
	done
	for intvlfile in `ls *.query`;do
		(python pysend.py query $intvlfile ipf >$intvlfile.send.stdout 2>$intvlfile.send.stderr &)
	done
	) >& /dev/null &' &
	#ssh -f $ip "cd $DIR; python pysend.py size $ip.back >& $ip.back.send"
	#for dip in `cat $IPF`;do
		#if [[ $ip != $dip ]];then
			#ssh -f $ip "cd $DIR; python pysend.py size $ip.back.$dip >& $ip.back.$dip.send"
		#fi
	#done
done

#echo 'starting QUERY sending' `date +%s.%N`
#for ip in `cat $IPF`;do
	#ssh -f $ip "cd $DIR; python pysend.py query $ip.query >& $ip.query.send"
#done
