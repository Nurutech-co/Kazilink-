import base64
from datetime import datetime
from typing import Any

import httpx

from app.core.config import settings


class MpesaError(Exception):
    pass


class MpesaService:
    def __init__(self):
        self.is_sandbox = settings.mpesa_environment.lower() == "sandbox"

        self.base_url = (
            "https://sandbox.safaricom.co.ke"
            if self.is_sandbox
            else "https://api.safaricom.co.ke"
        )

    def _check_config(self):
        required = {
            "MPESA_CONSUMER_KEY": settings.mpesa_consumer_key,
            "MPESA_CONSUMER_SECRET": settings.mpesa_consumer_secret,
            "MPESA_SHORTCODE": settings.mpesa_shortcode,
            "MPESA_PASSKEY": settings.mpesa_passkey,
            "MPESA_CALLBACK_URL": settings.mpesa_callback_url,
        }

        missing = [name for name, value in required.items() if not value]

        if missing:
            raise MpesaError(
                "Missing Daraja configuration: " + ", ".join(missing)
            )

    async def access_token(self) -> str:
        self._check_config()

        credentials = (
            f"{settings.mpesa_consumer_key}:"
            f"{settings.mpesa_consumer_secret}"
        )

        encoded = base64.b64encode(credentials.encode()).decode()

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{self.base_url}/oauth/v1/generate"
                "?grant_type=client_credentials",
                headers={
                    "Authorization": f"Basic {encoded}",
                },
            )

        if response.status_code >= 400:
            raise MpesaError(
                f"Daraja OAuth failed: {response.status_code} "
                f"{response.text}"
            )

        data = response.json()

        if "access_token" not in data:
            raise MpesaError("Daraja did not return an access token")

        return data["access_token"]

    def _password(self) -> tuple[str, str]:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        raw = (
            f"{settings.mpesa_shortcode}"
            f"{settings.mpesa_passkey}"
            f"{timestamp}"
        )

        password = base64.b64encode(raw.encode()).decode()

        return password, timestamp

    async def stk_push(
        self,
        phone_number: str,
        amount: int,
        account_reference: str | None = None,
        description: str | None = None,
    ) -> dict[str, Any]:

        if amount <= 0:
            raise MpesaError("Amount must be greater than zero")

        token = await self.access_token()

        password, timestamp = self._password()

        payload = {
            "BusinessShortCode": settings.mpesa_shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount),
            "PartyA": phone_number,
            "PartyB": settings.mpesa_shortcode,
            "PhoneNumber": phone_number,
            "CallBackURL": settings.mpesa_callback_url,
            "AccountReference": (
                account_reference
                or settings.mpesa_account_reference
            ),
            "TransactionDesc": (
                description
                or settings.mpesa_transaction_description
            ),
        }

        async with httpx.AsyncClient(timeout=45) as client:
            response = await client.post(
                f"{self.base_url}/mpesa/stkpush/v1/processrequest",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )

        if response.status_code >= 400:
            raise MpesaError(
                f"Daraja STK Push failed: {response.status_code} "
                f"{response.text}"
            )

        data = response.json()

        return data


mpesa = MpesaService()
