#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")"

for i in tests/*.sh; do
  echo
  echo -e "\e[33;1mRunning $i\e[m"
  python3 bs.py $i > $i.result ||:
  [ -f $i.expected ] || cp $i.result $i.expected
  [ -f $i.expected ] && {
    diff -u $i.expected $i.result --color || {
      read -n 1 -p "[$i] Accept changes [y|N]? " ACCEPT
      [ "${ACCEPT:0:1}" = "y" ] && {
          echo
          cp -v $i.result $i.expected
      }
    }
  }
done
