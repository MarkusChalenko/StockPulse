import contextvars
import logging

request_id_ctx_var = contextvars.ContextVar("request_id", default=None)
request_path_ctx_var = contextvars.ContextVar("request_path", default=None)


class RequestContextFilter(logging.Filter):
    """
    Logging filter that injects request-specific context into log records.

    Adds attributes:
        request_id (str): Unique request identifier.
        request_path (str): Path of the HTTP request.
    """
    def filter(self, record):
        record.request_id = request_id_ctx_var.get() or "N/A"
        record.request_path = request_path_ctx_var.get() or "N/A"
        return True


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "%(levelname)s: %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S%z"
        },
        "detailed": {
            "format": "[%(asctime)s] [%(levelname)s|%(module)s|L%(lineno)d] [%(request_id)s] [%(request_path)s] %("
                      "message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S%z"
        }
    },
    "filters": {
        "request_id_filter": {
            '()': RequestContextFilter
        }
    },
    "handlers": {
        "stderr": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "filters": ["request_id_filter"],
            "stream": "ext://sys.stderr"
        },
    },
    
    "root": {
        "level": "DEBUG",
        "handlers": [
            "stderr",
        ]
    }
}
