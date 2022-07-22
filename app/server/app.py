from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm


from server.routes.user import router as UserRouter
from server.routes.product import router as ProductRouter
from server.routes.basket import router as BasketRouter

app = FastAPI()


app.include_router(UserRouter, tags=["User"], prefix="/user")
app.include_router(ProductRouter, tags=["Product"], prefix="/Product")
app.include_router(BasketRouter, tags=["Basket"], prefix="/Basket")

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to this fantastic app!"}
