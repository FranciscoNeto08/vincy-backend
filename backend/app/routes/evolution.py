# app/routes/evolution.py

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.config.security import get_current_user
from app.models.user import User
from app.schemas.evolution import (
    EvolutionConfigCreate,
    EvolutionConfigResponse,
    EvolutionTestConnection,
    WhatsAppMessageResponse,
    WhatsAppMessageSend,
    WhatsAppCampaignRequest,
)
from app.services import evolution_service
from app.config.settings import settings
from app.utils.audit import audit_event
from app.utils.rate_limit import campaign_limiter

router = APIRouter(prefix="/evolution", tags=["WhatsApp Integration"])


@router.post(
    "/config",
    response_model=EvolutionConfigResponse,
    status_code=status.HTTP_201_CREATED,
)
def setup_evolution_config(
    data: EvolutionConfigCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Configura as credenciais da Evolution API.
    
    **Requer:**
    - `api_key`: Sua chave de API da Evolution
    - `base_url`: URL da instância da Evolution (ex: https://sua-instancia.evolution.api/)
    - `instance_name`: Nome da instância (padrão: "default")
    """
    config = evolution_service.save_evolution_config(
        db, current_user.id, data
    )
    return config


@router.get(
    "/config",
    response_model=EvolutionConfigResponse,
    status_code=status.HTTP_200_OK,
)
def get_evolution_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtém a configuração atual da Evolution API."""
    config = evolution_service.get_evolution_config(db, current_user.id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhuma configuração da Evolution API encontrada.",
        )
    return config


@router.post(
    "/test-connection",
    response_model=EvolutionTestConnection,
)
def test_evolution_connection(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Testa a conexão com a Evolution API.
    
    Retorna o status da instância se a conexão for bem-sucedida.
    """
    try:
        result = evolution_service.test_evolution_connection(db, current_user.id)
        return EvolutionTestConnection(
            success=result.get("success", False),
            connected=result.get("success", False),
            instance_status=str(result.get("data", {})),
            error=result.get("error"),
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        return EvolutionTestConnection(
            success=False,
            connected=False,
            error=str(e),
        )


@router.post(
    "/send-message",
    response_model=WhatsAppMessageResponse,
)
def send_whatsapp_message(
    data: WhatsAppMessageSend,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Envia uma mensagem via WhatsApp usando Evolution API.
    
    **Requer:**
    - `phone`: Número do telefone (com ou sem formatação)
    - `message`: Texto da mensagem
    
    **Exemplo:**
    ```json
    {
        "phone": "(92) 98765-4321",
        "message": "Olá! Esta é uma mensagem de teste."
    }
    ```
    """
    result = evolution_service.send_whatsapp_message(
        db, current_user.id, data.phone, data.message
    )

    return WhatsAppMessageResponse(
        success=result.get("success", False),
        phone=result.get("phone"),
        message_id=result.get("data", {}).get("key", {}).get("id") if result.get("success") else None,
        error=result.get("error"),
    )


@router.delete(
    "/config",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_evolution_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Desativa a configuração da Evolution API."""
    config = evolution_service.get_evolution_config(db, current_user.id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhuma configuração encontrada.",
        )
    
    config.active = False
    db.commit()


@router.post("/send-campaign-whatsapp", response_model=dict)
def send_whatsapp_campaign(
    data: WhatsAppCampaignRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    allowed, retry_after = campaign_limiter.hit(
        f"whatsapp:{current_user.id}",
        settings.CAMPAIGN_RATE_LIMIT_PER_MINUTE,
        60,
    )
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Muitos envios em pouco tempo. Aguarde e tente novamente.",
            headers={"Retry-After": str(retry_after)},
        )

    from sqlalchemy import func
    from datetime import datetime, timezone
    from app.models.campaign import Campaign
    from app.models.client import Client

    query = db.query(Client).filter(Client.owner_id == current_user.id)
    if data.client_ids is not None:
        query = query.filter(Client.id.in_(data.client_ids))

    clients = query.limit(settings.MAX_CAMPAIGN_RECIPIENTS + 1).all()
    if len(clients) > settings.MAX_CAMPAIGN_RECIPIENTS:
        raise HTTPException(status_code=400, detail="Quantidade de destinatários acima do limite permitido.")
    clients = [c for c in clients if c.phone]

    if not clients:
        raise HTTPException(status_code=400, detail="Nenhum cliente selecionado possui telefone cadastrado.")

    start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    daily = int(
        db.query(func.coalesce(func.sum(Campaign.total_destinatarios), 0))
        .filter(Campaign.owner_id == current_user.id, Campaign.created_at >= start)
        .scalar() or 0
    )
    if daily + len(clients) > settings.CAMPAIGN_DAILY_RECIPIENT_LIMIT:
        raise HTTPException(status_code=429, detail="Limite diário de destinatários atingido.")

    resultados = []
    total_enviados = 0
    total_falhas = 0

    for cliente in clients:
        msg_personalizada = data.message.replace("{nome}", cliente.name or "Cliente")
        result = evolution_service.send_whatsapp_message(
            db, current_user.id, cliente.phone, msg_personalizada
        )
        ok = bool(result.get("success"))
        total_enviados += int(ok)
        total_falhas += int(not ok)
        resultados.append({
            "client_id": cliente.id,
            "client_name": cliente.name,
            "phone": cliente.phone,
            "success": ok,
            **({"error": "Falha no envio."} if not ok else {}),
        })

    campaign = Campaign(
        channel="whatsapp",
        subject=data.subject,
        message=data.message,
        total_destinatarios=len(clients),
        total_enviados=total_enviados,
        total_falhas=total_falhas,
        owner_id=current_user.id,
    )
    db.add(campaign)
    db.commit()

    audit_event(
        db,
        action="whatsapp.campaign",
        user_id=current_user.id,
        owner_id=current_user.id,
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        request_id=request.scope.get("vynce.request_id"),
        detail=f"destinatarios={len(clients)}; enviados={total_enviados}; falhas={total_falhas}",
    )

    return {
        "total_destinatarios": len(clients),
        "total_enviados": total_enviados,
        "total_falhas": total_falhas,
        "resultados": resultados,
    }
