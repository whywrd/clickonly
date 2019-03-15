#!/bin/bash
su will -c 'pg_ctl -D /usr/local/var/postgres start'
su will -c 'createdb redirect_usage'
su will -c 'pg_ctl -D /usr/local/var/postgres stop'
