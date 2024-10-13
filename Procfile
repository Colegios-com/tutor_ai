web: gunicorn --worker-tmp-dir /dev/shm --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8080 --timeout 100 main:app
