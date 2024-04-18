Start the server

For development
```
devtools-server runserver
```

For production
```
gunicorn devtools_server.server:application
```

Create a collection

```
curl -v -O -J --header "Content-Type: application/json" \
  --data '{"collection":"namespace.name", "project": "collection"}' \
  "localhost:8000/v1/creator/collection"
```

Create a playbook

```
curl -v -O -J --header "Content-Type: application/json" \
  --data '{"project":"ansible-project", "scm_org":"ansible", "scm_project": "devops"}' \
  "localhost:8000/v1/creator/playbook"
```
