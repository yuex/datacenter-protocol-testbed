#!/bin/sh
rm log/*.std{out,err}
for ip in `cat ipf`;do
	scp $ip:sab/misc/*.stdout log;
done
for ip in `cat ipf`;do
	scp $ip:sab/misc/*.stderr log;
done
#ls -l log/*.stderr|less
