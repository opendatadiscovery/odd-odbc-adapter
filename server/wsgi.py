import os
from logging.config import dictConfig
from flask import Response
from odd_contract import init_flask_app, init_controller
from adapter.adapter import create_adapter
from app.cache import Cache
from app.controller import Controller
from app.scheduler import Scheduler

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})


def create_app(conf):
    app = init_flask_app()
    app.config.from_object(conf)

    app.add_url_rule("/health", "healthcheck", lambda: Response(status=200))

    cache = Cache()
    adapter = create_adapter()
    init_controller(Controller(adapter, cache))

    cache_refresh_interval: int = int(app.config["SCHEDULER_INTERVAL_MINUTES"])
    with app.app_context():
        Scheduler(adapter, cache).start_scheduler(cache_refresh_interval)
        return app


application = create_app(os.environ.get("FLASK_CONFIG") or "config.DevelopmentConfig")
