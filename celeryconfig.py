from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = 'mysql://sql12722367:73DvxQuh72@sql12.freesqldatabase.com:3306/sql12722367'
    CELERY_BROKER_URL: str = "redis-14766.c98.us-east-1-4.ec2.redns.redis-cloud.com:14766"
    CELERY_RESULT_BACKEND: str = "redis-14766.c98.us-east-1-4.ec2.redns.redis-cloud.com:14766"

settings = Settings()
