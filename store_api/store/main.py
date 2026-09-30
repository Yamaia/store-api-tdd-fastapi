from fastapi import FastAPI

from store.controllers.product import router as product_router
from store.core.config import settings

app = FastAPI(title=settings.title, version=settings.version, root_path=settings.root_path)
app.include_router(product_router)
