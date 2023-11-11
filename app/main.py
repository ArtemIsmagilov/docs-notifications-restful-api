from fastapi import FastAPI

from app.routers import notifications
import uvicorn

app = FastAPI()
app.include_router(notifications.router)

if __name__ == '__main__':
    uvicorn.run('app.main:app', host='0.0.0.0', port=8000)
