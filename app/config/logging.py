import logging, sys, json, time
from typing import Any, MutableMapping

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        data: MutableMapping[str, Any] = {
            "ts": int(time.time()*1000),
            "lvl": record.levelname,
            "msg": record.getMessage(),
            "logger": record.name,
        }
        for k in ("tenant_id", "corr_id"):
            if hasattr(record, k):
                data[k] = getattr(record, k)
        return json.dumps(data, ensure_ascii=False)

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JsonFormatter())

logging.basicConfig(level=logging.INFO, handlers=[handler])
