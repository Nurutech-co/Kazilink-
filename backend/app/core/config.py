from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
DARAJA_ENV=Path(__file__).resolve().parents[2]/"config"/"daraja.env"
class Settings(BaseSettings):
    app_env:str="development"; database_url:str=""; jwt_secret:str="CHANGE_ME"
    mpesa_environment:str="sandbox"; mpesa_consumer_key:str=""; mpesa_consumer_secret:str=""
    mpesa_shortcode:str=""; mpesa_passkey:str=""; mpesa_callback_url:str=""
    mpesa_account_reference:str="KaziLink"; mpesa_transaction_description:str="KaziLink Payment"
    model_config=SettingsConfigDict(env_file=DARAJA_ENV,env_file_encoding="utf-8",extra="ignore")
settings=Settings()
