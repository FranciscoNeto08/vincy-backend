from datetime import datetime, timezone


def utcnow() -> datetime:
    """Retorna o horário atual em UTC (timezone-aware)."""
    return datetime.now(timezone.utc)


def to_float(value, default: float = 0.0) -> float:
    """Converte valores possivelmente None/str para float com segurança."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def paginate(query, page: int = 1, page_size: int = 20):
    """Aplica paginação simples a uma query do SQLAlchemy."""
    page = max(page, 1)
    page_size = max(min(page_size, 100), 1)
    return query.offset((page - 1) * page_size).limit(page_size)
