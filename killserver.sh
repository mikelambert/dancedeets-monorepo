ps ux | grep python_runtime | grep -v grep | cut -f2 -d' ' | xargs kill -9 
