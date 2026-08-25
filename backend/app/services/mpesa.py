import base64
from datetime import datetime
import httpx
from app.core.config import settings
class MpesaError(Exception): pass
class MpesaService:
    def __init__(self):
        self.base_url="https://sandbox.safaricom.co.ke" if settings.mpesa_environment.lower()=="sandbox" else "https://api.safaricom.co.ke"
    def check(self):
        vals={"MPESA_CONSUMER_KEY":settings.mpesa_consumer_key,"MPESA_CONSUMER_SECRET":settings.mpesa_consumer_secret,"MPESA_SHORTCODE":settings.mpesa_shortcode,"MPESA_PASSKEY":settings.mpesa_passkey,"MPESA_CALLBACK_URL":settings.mpesa_callback_url}
        missing=[k for k,v in vals.items() if not v]
        if missing: raise MpesaError("Missing Daraja configuration: "+", ".join(missing))
    async def token(self):
        self.check(); raw=f"{settings.mpesa_consumer_key}:{settings.mpesa_consumer_secret}"
        enc=base64.b64encode(raw.encode()).decode()
        async with httpx.AsyncClient(timeout=30) as c:r=await c.get(f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials",headers={"Authorization":f"Basic {enc}"})
        if r.status_code>=400: raise MpesaError(f"Daraja OAuth failed: {r.status_code} {r.text}")
        return r.json()["access_token"]
    async def stk_push(self,phone_number,amount,account_reference=None,description=None):
        if amount<=0: raise MpesaError("Amount must be greater than zero")
        token=await self.token(); ts=datetime.now().strftime("%Y%m%d%H%M%S")
        raw=f"{settings.mpesa_shortcode}{settings.mpesa_passkey}{ts}"
        password=base64.b64encode(raw.encode()).decode()
        payload={"BusinessShortCode":settings.mpesa_shortcode,"Password":password,"Timestamp":ts,"TransactionType":"CustomerPayBillOnline","Amount":int(amount),"PartyA":phone_number,"PartyB":settings.mpesa_shortcode,"PhoneNumber":phone_number,"CallBackURL":settings.mpesa_callback_url,"AccountReference":account_reference or settings.mpesa_account_reference,"TransactionDesc":description or settings.mpesa_transaction_description}
        async with httpx.AsyncClient(timeout=45) as c:r=await c.post(f"{self.base_url}/mpesa/stkpush/v1/processrequest",headers={"Authorization":f"Bearer {token}","Content-Type":"application/json"},json=payload)
        if r.status_code>=400: raise MpesaError(f"Daraja STK Push failed: {r.status_code} {r.text}")
        return r.json()
mpesa=MpesaService()
