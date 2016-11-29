key=$(grep scrapinghub_key keys.yaml | awk '{gsub(/"/, "", $2); print $2}')
echo $key | shub login
shub deploy
