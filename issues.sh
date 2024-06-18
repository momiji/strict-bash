#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")"

for i in issues/*.sh; do
  # bash
  echo -e "\e[33;1mRunning bash $i\e[m"
  cat issues/header-bash $i issues/footer > $i.test
  chmod +x $i.test
  rc=0
  $i.test || rc=$?
  [ $rc = 1 ] || {
    echo do something
  }
  # # ksh
  # cat issues/header-zsh $i issues/footer > $i.zsh
  # sed -i 's/##//g' $i.zsh
  # chmod +x $i.zsh
  # echo -e "\e[33;1mRunning zsh $i\e[m"
  # rc=0
  # $i.zsh || rc=$?
  # [ $rc = 1 ] || {
  #   echo do something
  # }
done
