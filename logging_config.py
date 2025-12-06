import logging
import json
import sys
from datetime import datetime
from typing import Optional


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        # Campos básicos de todo log
        log_record = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Campos extras (se existirem no record.extra)
        for attr in (
            "client_ip",
            "method",
            "path",
            "status_code",
            "request_id",
            "duration_ms",
            "database",
            "collection",
            "total_clientes",
            "event",
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

    Isso é chamado automaticamente pelo get_logger().
    """
    global _configured
    if _configured:
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    root = logging.getLogger()
    root.setLevel(logging.INFO)

    # Zera handlers anteriores e coloca só o nosso handler JSON
    root.handlers = [handler]

    _configured = True


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Retorna um logger já configurado para emitir JSON.

    Uso:
        from logging_config import get_logger
        logger = get_logger(__name__)
        logger.info("mensagem", extra={"event": "algo_importante"})
    """
    _configure_root_logger()
    return logging.getLogger(name or "clientes_api")
