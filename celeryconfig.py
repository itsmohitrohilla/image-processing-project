from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    CELERY_BROKER_URL: str ='redis://:1VZKf8Oi3V6BSua1fT5PQNOofKinlvye@redis-14766.c98.us-east-1-4.ec2.redns.redis-cloud.com:14766/0'
    CELERY_RESULT_BACKEND: str = 'redis://:1VZKf8Oi3V6BSua1fT5PQNOofKinlvye@redis-14766.c98.us-east-1-4.ec2.redns.redis-cloud.com:14766/0'

settings = Settings()


#redis-14766.c98.us-east-1-4.ec2.redns.redis-cloud.com:14766

#celery -A app.tasks worker --loglevel=info
#uvicorn app.main:app --reload