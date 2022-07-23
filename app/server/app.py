from datetime import datetime, timedelta
from typing import Union

from fastapi import FastAPI, HTTPException, status, Depends, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.encoders import jsonable_encoder
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from server.database import (add_basket, delete_basket, retrieve_basket, retrieve_baskets,update_basket,
    add_product, delete_product, retrieve_product, retrieve_products, update_product)

from server.models.basket import ( ErrorResponseModel, ResponseModel, BasketSchema, UpdateBasketModel,)
from server.models.product import ( ProductSchema, UpdateProductModel)

from server.database import (
    add_user,
    delete_user,
    retrieve_user,
    retrieve_users,
    update_user,
)
from server.models.user import ( UserSchema, UpdateUserModel)

from .database import user_collection 


# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


user_collection = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    }
}


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None


class User(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None


class UserInDB(User):
    hashed_password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(db, username: str, password: str):
    user = get_user(db,username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

app = FastAPI()

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(user_collection,form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/product", tags=["product"],response_description="product data added into the database")
async def add_product_data(product: ProductSchema = Body(...), current_uer: User = Depends(get_current_active_user)):
    product = jsonable_encoder(product)
    new_product = await add_product(product)
    return ResponseModel(new_product, "product added successfully.")


@app.get("/product", tags=["product"],response_description="products retrieved")
async def get_products( current_uer: User = Depends(get_current_active_user)):
    products = await retrieve_products()
    if products:
        return ResponseModel(products, "products data retrieved successfully")
    return ResponseModel(products, "Empty list returned")


@app.get("/product/{id}", tags=["product"],response_description="product data retrieved")
async def get_product_data(id, current_uer: User = Depends(get_current_active_user)):
    product = await retrieve_product(id)
    if product:
        return ResponseModel(product, "product data retrieved successfully")
    return ErrorResponseModel("An error occurred.", 404, "product doesn't exist.")


@app.put("/product/{id}", tags=["product"])
async def update_product_data(id: str, req: UpdateProductModel = Body(...), current_uer: User = Depends(get_current_active_user)):
    req = {k: v for k, v in req.dict().items() if v is not None}
    updated_product = await update_product(id, req)
    if updated_product:
        return ResponseModel(
            "product with ID: {} name update is successful".format(id),
            "product name updated successfully",
        )
    return ErrorResponseModel(
        "An error occurred",
        404,
        "There was an error updating the product data.",
    )


@app.delete("product/{id}", tags=["product"],response_description="product data deleted from the database")
async def delete_product_data(id: str, current_uer: User = Depends(get_current_active_user)):
    deleted_product = await delete_product(id)
    if deleted_product:
        return ResponseModel(
            "product with ID: {} removed".format(id), "product deleted successfully"
        )
    return ErrorResponseModel(
        "An error occurred", 404, "product with id {0} doesn't exist".format(id)
    )

@app.post("/basket", tags=["Basket"],response_description="basket data added into the database")
async def add_basket_data(basket: BasketSchema = Body(...), current_uer: User = Depends(get_current_active_user)):
    basket = jsonable_encoder(basket)
    new_basket = await add_basket(basket)
    return ResponseModel(new_basket, "basket added successfully.")


@app.get("/basket", tags=["Basket"],response_description="baskets retrieved")
async def get_baskets( current_uer: User = Depends(get_current_active_user)):
    baskets = await retrieve_baskets()
    if baskets:
        return ResponseModel(baskets, "baskets data retrieved successfully")
    return ResponseModel(baskets, "Empty list returned")


@app.get("/basket/{id}", tags=["Basket"],response_description="basket data retrieved")
async def get_basket_data(id, current_uer: User = Depends(get_current_active_user)):
    basket = await retrieve_basket(id)
    if basket:
        return ResponseModel(basket, "basket data retrieved successfully")
    return ErrorResponseModel("An error occurred.", 404, "basket doesn't exist.")


@app.put("/basket/{id}",tags=["Basket"])
async def update_basket_data(id: str, req: UpdateBasketModel = Body(...), current_uer: User = Depends(get_current_active_user)):
    req = {k: v for k, v in req.dict().items() if v is not None}
    updated_basket = await update_basket(id, req)
    if updated_basket:
        return ResponseModel(
            "basket with ID: {} name update is successful".format(id),
            "basket name updated successfully",
        )
    return ErrorResponseModel(
        "An error occurred",
        404,
        "There was an error updating the basket data.",
    )

@app.delete("basket/{id}", tags=["Basket"],response_description="basket data deleted from the database")
async def delete_basket_data(id: str, current_uer: User = Depends(get_current_active_user)):
    deleted_basket = await delete_basket(id)
    if deleted_basket:
        return ResponseModel(
            "basket with ID: {} removed".format(id), "basket deleted successfully"
        )
    return ErrorResponseModel(
        "An error occurred", 404, "basket with id {0} doesn't exist".format(id)
    )

@app.post("/user", tags=["user"], response_description="user data added into the database")
async def add_user_data(user: UserSchema = Body(...)):
    user = jsonable_encoder(user)
    user["hashed_password"]=get_password_hash(user["hashed_password"])
    new_user = await add_user(user)
    return ResponseModel(new_user, "user added successfully.")


@app.get("/user", tags=["user"], response_description="users retrieved")
async def get_users():
    users = await retrieve_users()
    if users:
        return ResponseModel(users, "users data retrieved successfully")
    return ResponseModel(users, "Empty list returned")


@app.get("/user/{id}", tags=["user"], response_description="user data retrieved")
async def get_user_data(id, current_uer: User = Depends(get_current_active_user)):
    user = await retrieve_user(id)
    if user:
        return ResponseModel(user, "user data retrieved successfully")
    return ErrorResponseModel("An error occurred.", 404, "user doesn't exist.")


@app.put("/user/{id}", tags=["user"])
async def update_user_data(id: str, req: UpdateUserModel = Body(...), current_uer: User = Depends(get_current_active_user)):
    req = {k: v for k, v in req.dict().items() if v is not None}
    updated_user = await update_user(id, req)
    if updated_user:
        return ResponseModel(
            "user with ID: {} name update is successful".format(id),
            "user name updated successfully",
        )
    return ErrorResponseModel(
        "An error occurred",
        404,
        "There was an error updating the user data.",
    )


@app.delete("/user/{id}", tags=["user"], response_description="user data deleted from the database")
async def delete_user_data(id: str, current_uer: User = Depends(get_current_active_user)):
    deleted_user = await delete_user(id)
    if deleted_user:
        return ResponseModel(
            "user with ID: {} removed".format(id), "user deleted successfully"
        )
    return ErrorResponseModel(
        "An error occurred", 404, "user with id {0} doesn't exist".format(id)
    )