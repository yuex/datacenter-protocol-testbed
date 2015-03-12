#!/usr/bin/env sh
#cat log/*.back.send.stdout |grep summary >$1.log.back
#cat log/*.query.send.stdout |grep summary >$1.log.query
cat log/*.back.recv.stdout >$1.log.back
cat log/*.query.send.stdout >$1.log.query
