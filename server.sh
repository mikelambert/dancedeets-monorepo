cat app.yaml | sed 's/runtime: vm/runtime: python27/' > app-devserver.yaml
echo 'libraries:
- name: ssl
  version: "latest"
' >> app-devserver.yaml
dev_appserver.py app-devserver.yaml --storage_path ~/Projects/dancedeets-storage/
