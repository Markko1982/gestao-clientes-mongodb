import logging
import json
import sys
from datetime import datetime
from typing import Optional


class JsonFormatter(logging.Formatter):
    """
    Formatter que converte o LogRecord em JSON.

    Exemplo de saída:
    {
      "timestamp": "...Z",
      "level": "INFO",
      "logger": "src.api",
      "message": "HTTP request",
      "event": "http_request",
      "method": "GET",
      "path": "/health",
      "status_code": 200,
      "duration_ms": 12.3
    }
    """

    def format(self, record: logging.LogRecord) -> str:
        # Campos básicos
        log_record = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Campos extras úteis que podemos adicionar via `extra={...}`
        for attr in (
            "event",
            "client_ip",
            "method",
            "path",
            "status_code",
            "request_id",
            "duration_ms",
            "database",
            "collection",
            "total_clientes",
        ):
            if hasattr(record, attr):
                log_record[attr] = getattr(record, attr)

        # Stacktrace em caso de erro
        if record.exc_info:
            log_record["exc_info"] = self.formatException(record.exc_info)

        return json.dumps(log_record, ensure_ascii=False)


_configured = False


def _configure_root_logger() -> None:
    """
    Configura o logger raiz apenas uma vez, usando JSON no stdout.
    """
    global _configured
    if _configured:
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    root = logging.getLogger()
    root.setLevel(logging.INFO)

    # Substitui handlers antigos pelo nosso
    root.handlers = [handler]

    _configured = True


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Retorna um logger já configurado para emitir JSON.

    Uso típico na API:
        from logging_config import get_logger
        logger = get_logger(__name__)
        logger.info("mensagem", extra={"event": "algo_importante"})
    """
    _configure_root_logger()
    return logging.getLogger(name or "clientes_api")
