release: python manage.py migrate && python manage.py collectstatic
web: daphne harvoldsite.asgi:application --port $PORT --bind 0.0.0.0 -v2
worker: python manage.py runworker channel_layer -v2