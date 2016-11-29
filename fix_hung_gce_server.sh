ps aux | grep vmboot | grep -v grep | awk '{print $2}' | xargs sudo kill -9 
