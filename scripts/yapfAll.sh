ls -l ../dataflow/ | grep '^d' | awk '{print $9}' | grep -v 'lib\|beam-master\|dist\|node_modules' | xargs -n1 ./yapf.sh --recursive --in-place
./yapf.sh --in-place --recursive ../dataflow/*.py

./yapf.sh --in-place --recursive ../scrapers
./yapf.sh --in-place --recursive ../scripts

ls -l ../server/ | grep '^d' | awk '{print $9}' | grep -v 'lib-\|node_modules\|node_server\|build\|frankenserver' | xargs -n1 ./yapf.sh --recursive --in-place
./yapf.sh --in-place --recursive ../server/*.py
