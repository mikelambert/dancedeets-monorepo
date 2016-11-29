# Used to generate example html files off our dev site, for eventual feeding into UnCSS plugin.
mkdir -p example_html/
curl http://dev.dancedeets.com:8080/new_homepage > example_html/new_homepage.html
