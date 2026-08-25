from fastapi import APIRouter,HTTPException
from pydantic import BaseModel,Field
from app.services.mpesa import mpesa,MpesaError
router=APIRouter()
class STKPushRequest(BaseModel):
    phone_number:str=Field(min_length=10,max_length=15); amount:int=Field(gt=0)
    account_reference:str|None=None; description:str|None=None
@router.post("/stk-push")
async def stk_push(req:STKPushRequest):
    try:return {"success":True,"data":await mpesa.stk_push(req.phone_number,req.amount,req.account_reference,req.description)}
    except MpesaError as e:raise HTTPException(status_code=502,detail=str(e))
@router.post("/callback")
async def callback(payload:dict):
    return {"ResultCode":0,"ResultDesc":"Callback received successfully"}
