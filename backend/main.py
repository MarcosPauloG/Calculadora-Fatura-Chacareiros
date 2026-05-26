from datetime import date
from typing import Dict, List, Literal, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="Calculadora Chacareiros API", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

INITIAL_PASSWORD = "Chacara2026"

USERS = {
    "admin": {"password": "Admin2026", "role": "admin", "must_change": False},
    "salvador": {"password": INITIAL_PASSWORD, "role": "user", "must_change": True, "nome": "SALVADOR CASER NETTO"},
    "christirson": {"password": INITIAL_PASSWORD, "role": "user", "must_change": True, "nome": "CHRISTIRSON PAULA DE ARAUJO"},
    "vidal": {"password": INITIAL_PASSWORD, "role": "user", "must_change": True, "nome": "FLAVIO VIDAL"},
    "milka": {"password": INITIAL_PASSWORD, "role": "user", "must_change": True, "nome": "MILKA VIANA FALCAO"},
    "girley": {"password": INITIAL_PASSWORD, "role": "user", "must_change": True, "nome": "GIRLEY NOGUEIRA DE JESUS (Cha-12)"},
    "fernando": {"password": INITIAL_PASSWORD, "role": "user", "must_change": True, "nome": "FERNANDO ANDRÉ DE SOUZA (Cha-16)"},
    "osmair": {"password": INITIAL_PASSWORD, "role": "user", "must_change": True, "nome": "OSMAIR TELES BUENO"},
    "weverton": {"password": INITIAL_PASSWORD, "role": "user", "must_change": True, "nome": "WEVERTON NUNES DA SILVA"},
    "luciane": {"password": INITIAL_PASSWORD, "role": "user", "must_change": True, "nome": "LUCIANE FERREIRA"},
    "paulo": {"password": INITIAL_PASSWORD, "role": "user", "must_change": True, "nome": "PAULO MARCOS DIAS (Cha-13)"},
}

READINGS: List[Dict] = []


class LoginInput(BaseModel):
    username: str
    password: str


class ChangePasswordInput(BaseModel):
    username: str
    current_password: str
    new_password: str


class ResetPasswordInput(BaseModel):
    admin_user: str
    admin_password: str
    target_user: str


class Reading(BaseModel):
    nome: str
    leitura_anterior: int = Field(ge=0)
    leitura_atual: int = Field(ge=0)


class InvoiceInput(BaseModel):
    referencia: str
    data_leitura: date
    valor_total: float = Field(gt=0)
    leitura_geral_anterior: int = Field(ge=0)
    leitura_geral_atual: int = Field(ge=0)
    participantes: List[Reading]


class BulkReadingInput(BaseModel):
    data_leitura: date
    referencia: str
    itens: List[Dict[str, Optional[str]]]
    n8n_webhook_url: Optional[str] = None


def validate_password(value: str) -> bool:
    return len(value) >= 8 and any(c.isalpha() for c in value) and any(c.isdigit() for c in value)


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/api/login")
def login(payload: LoginInput):
    user = USERS.get(payload.username.lower())
    if not user or user["password"] != payload.password:
        raise HTTPException(status_code=401, detail="Usuário ou senha inválidos")
    return {
        "username": payload.username.lower(),
        "role": user["role"],
        "must_change_password": user.get("must_change", False),
        "nome": user.get("nome", "Administrador"),
    }


@app.post("/api/change-password")
def change_password(payload: ChangePasswordInput):
    user = USERS.get(payload.username.lower())
    if not user or user["password"] != payload.current_password:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    if not validate_password(payload.new_password):
        raise HTTPException(status_code=400, detail="Senha deve ser alfanumérica e ter ao menos 8 caracteres")
    user["password"] = payload.new_password
    user["must_change"] = False
    return {"ok": True}


@app.post("/api/admin/reset-password")
def admin_reset_password(payload: ResetPasswordInput):
    admin = USERS.get(payload.admin_user.lower())
    if not admin or admin["role"] != "admin" or admin["password"] != payload.admin_password:
        raise HTTPException(status_code=401, detail="Admin inválido")
    target = USERS.get(payload.target_user.lower())
    if not target:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    target["password"] = INITIAL_PASSWORD
    target["must_change"] = True
    return {"ok": True, "temp_password": INITIAL_PASSWORD}


@app.post("/api/readings/bulk")
def save_bulk_readings(payload: BulkReadingInput):
    for item in payload.itens:
        item["data_leitura"] = str(payload.data_leitura)
        item["referencia"] = payload.referencia
    READINGS.extend(payload.itens)
    return {
        "ok": True,
        "saved": len(payload.itens),
        "message": "Salvo. Envie as fotos para o Drive via n8n usando o campo foto_url/arquivo.",
        "n8n_webhook_url": payload.n8n_webhook_url,
    }


@app.post("/api/rateio")
def calcular_rateio(payload: InvoiceInput):
    consumos = []
    for p in payload.participantes:
        consumo = p.leitura_atual - p.leitura_anterior
        if consumo < 0:
            raise HTTPException(status_code=400, detail=f"Leitura inválida para {p.nome}: atual menor que anterior")
        consumos.append({"nome": p.nome, "consumo": consumo})

    total_individual = sum(c["consumo"] for c in consumos)
    consumo_geral = payload.leitura_geral_atual - payload.leitura_geral_anterior
    diferenca = consumo_geral - total_individual

    if total_individual <= 0:
        raise HTTPException(status_code=400, detail="Soma de consumos individuais deve ser maior que zero")

    rateio = []
    for item in consumos:
        percentual = item["consumo"] / total_individual
        consumo_com_ajuste = item["consumo"] + (diferenca * percentual)
        valor = payload.valor_total * percentual
        rateio.append({
            "nome": item["nome"],
            "consumo_kwh": round(item["consumo"], 2),
            "percentual": round(percentual * 100, 2),
            "consumo_ajustado_kwh": round(consumo_com_ajuste, 2),
            "valor_rs": round(valor, 2),
        })

    return {
        "referencia": payload.referencia,
        "consumo_geral": consumo_geral,
        "total_individual": total_individual,
        "diferenca_kwh": diferenca,
        "valor_total": payload.valor_total,
        "rateio": rateio,
    }
