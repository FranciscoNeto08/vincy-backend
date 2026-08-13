"""Integração segura com Evolution API."""
from __future__ import annotations

import re
import requests
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.models.client import Client
from app.models.evolution import EvolutionConfig
from app.schemas.evolution import EvolutionConfigCreate
from app.utils.ssrf import SSRFValidationError, validate_outbound_url


def _normalize_phone(phone: str) -> str:
    digits = "".join(ch for ch in str(phone) if ch.isdigit())
    if len(digits) in (10, 11):
        digits = "55" + digits
    if not digits.startswith("55") or len(digits) < 12 or len(digits) > 13:
        raise ValueError("Número de telefone inválido.")
    return digits


class EvolutionAPI:
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = validate_outbound_url(
            base_url, allow_private=settings.EVOLUTION_ALLOW_PRIVATE_TARGETS
        )
        self.headers = {"Content-Type": "application/json", "apikey": api_key}

    def _url(self, path: str) -> str:
        # Revalida antes de cada chamada para não confiar somente no valor salvo.
        base = validate_outbound_url(
            self.base_url, allow_private=settings.EVOLUTION_ALLOW_PRIVATE_TARGETS
        )
        return f"{base}/{path.lstrip('/')}"

    def send_message(self, phone: str, message: str, instance_name: str = "default") -> dict:
        try:
            numero = _normalize_phone(phone)
            response = requests.post(
                self._url(f"message/sendText/{instance_name}"),
                json={"number": numero, "text": message},
                headers=self.headers,
                timeout=10,
            )
            if response.status_code not in (200, 201):
                return {"success": False, "error": "Evolution API recusou o envio.", "status_code": response.status_code}
            try:
                data = response.json()
            except ValueError:
                data = {}
            return {"success": True, "data": data, "phone": numero}
        except (ValueError, SSRFValidationError) as exc:
            return {"success": False, "error": str(exc)}
        except requests.exceptions.Timeout:
            return {"success": False, "error": "Timeout ao enviar mensagem."}
        except requests.exceptions.RequestException:
            return {"success": False, "error": "Falha de comunicação com a Evolution API."}

    def send_media(self, phone: str, media_url: str, caption: str = "", instance_name: str = "default") -> dict:
        try:
            numero = _normalize_phone(phone)
            safe_media_url = validate_outbound_url(
                media_url, allow_private=settings.EVOLUTION_ALLOW_PRIVATE_TARGETS
            )
            response = requests.post(
                self._url(f"message/sendMedia/{instance_name}"),
                json={"number": numero, "mediaType": "image", "media": safe_media_url, "caption": caption},
                headers=self.headers,
                timeout=10,
            )
            if response.status_code not in (200, 201):
                return {"success": False, "error": "Evolution API recusou o envio.", "status_code": response.status_code}
            try:
                data = response.json()
            except ValueError:
                data = {}
            return {"success": True, "data": data, "phone": numero}
        except (ValueError, SSRFValidationError) as exc:
            return {"success": False, "error": str(exc)}
        except requests.exceptions.RequestException:
            return {"success": False, "error": "Falha de comunicação com a Evolution API."}

    def send_template(self, phone: str, template_name: str, params: list | None = None, instance_name: str = "default") -> dict:
        try:
            numero = _normalize_phone(phone)
            if not re.fullmatch(r"[A-Za-z0-9._-]{1,100}", template_name):
                raise ValueError("Nome de template inválido.")
            response = requests.post(
                self._url(f"message/sendTemplate/{instance_name}"),
                json={"number": numero, "template": {"name": template_name, "parameters": {"body": {"parameters": params or []}}}},
                headers=self.headers,
                timeout=10,
            )
            if response.status_code not in (200, 201):
                return {"success": False, "error": "Evolution API recusou o envio.", "status_code": response.status_code}
            try:
                data = response.json()
            except ValueError:
                data = {}
            return {"success": True, "data": data, "phone": numero}
        except (ValueError, SSRFValidationError) as exc:
            return {"success": False, "error": str(exc)}
        except requests.exceptions.RequestException:
            return {"success": False, "error": "Falha de comunicação com a Evolution API."}

    def get_instance_status(self, instance_name: str = "default") -> dict:
        try:
            response = requests.get(
                self._url("instance/fetchInstances"),
                headers=self.headers,
                timeout=10,
            )
            if response.status_code != 200:
                return {"success": False, "error": "Não foi possível obter o status da instância."}
            try:
                data = response.json()
            except ValueError:
                data = {}
            return {"success": True, "data": data}
        except SSRFValidationError as exc:
            return {"success": False, "error": str(exc)}
        except requests.exceptions.RequestException:
            return {"success": False, "error": "Falha de comunicação com a Evolution API."}


def get_evolution_config(db: Session, owner_id: int) -> EvolutionConfig | None:
    return db.query(EvolutionConfig).filter(
        EvolutionConfig.owner_id == owner_id,
        EvolutionConfig.active.is_(True),
    ).first()


def save_evolution_config(db: Session, owner_id: int, data: EvolutionConfigCreate) -> EvolutionConfig:
    try:
        safe_url = validate_outbound_url(
            str(data.base_url), allow_private=settings.EVOLUTION_ALLOW_PRIVATE_TARGETS
        )
    except SSRFValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    db.query(EvolutionConfig).filter(EvolutionConfig.owner_id == owner_id).update({"active": False})
    config = EvolutionConfig(
        owner_id=owner_id,
        api_key=data.api_key,
        base_url=safe_url,
        instance_name=data.instance_name or "default",
        active=True,
    )
    db.add(config)
    db.commit()
    db.refresh(config)
    return config


def test_evolution_connection(db: Session, owner_id: int) -> dict:
    config = get_evolution_config(db, owner_id)
    if not config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nenhuma configuração da Evolution API encontrada.")
    return EvolutionAPI(config.api_key, config.base_url).get_instance_status(config.instance_name)


def send_whatsapp_message(db: Session, owner_id: int, phone: str, message: str) -> dict:
    config = get_evolution_config(db, owner_id)
    if not config:
        return {"success": False, "error": "Evolution API não configurada. Verifique as configurações."}
    return EvolutionAPI(config.api_key, config.base_url).send_message(phone, message, config.instance_name)


def send_whatsapp_media(db: Session, owner_id: int, phone: str, media_url: str, caption: str = "") -> dict:
    config = get_evolution_config(db, owner_id)
    if not config:
        return {"success": False, "error": "Evolution API não configurada."}
    return EvolutionAPI(config.api_key, config.base_url).send_media(phone, media_url, caption, config.instance_name)
