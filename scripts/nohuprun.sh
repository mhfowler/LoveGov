NOHUPLOG="/log/nohup.out"

echo $0 $1 $2 $3 $4 $5 $6 $7 $8 $9 > $NOHUPLOG
echo "$(date)" >> $NOHUPLOG
echo " " >> $NOHUPLOG
nohup $1 $2 $3 $4 $5 $6 $7 $8 $9  >> $NOHUPLOG &