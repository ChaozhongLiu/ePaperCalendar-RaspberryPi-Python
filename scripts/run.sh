VAR_1=$(date +%Y%m%d)
cd ~/ePaperCalendar/scripts/
nohup sudo python3 -u WeatherStation.py > log_${VAR_1}.txt 2>&1 &