
hline(){
   printf -- '-%.0s' {1..100};printf "\n"
}

hline
ev3dev -h
hline
for cmd in  list upload download delete cleanup mirror rmdir mkdir start stop install_logging install_rpyc_server
do
  ev3dev $cmd -h
  hline
done