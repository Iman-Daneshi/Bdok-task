from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder

from server.database import (
    add_product,
    delete_product,
    retrieve_product,
    retrieve_products,
    update_product,
)
from server.models.product import (
    ErrorResponseModel,
    ResponseModel,
    ProductSchema,
    UpdateProductModel,
)

router = APIRouter()


@router.post("/", response_description="product data added into the database")
async def add_product_data(product: ProductSchema = Body(...)):
    product = jsonable_encoder(product)
    new_product = await add_product(product)
    return ResponseModel(new_product, "product added successfully.")


@router.get("/", response_description="products retrieved")
async def get_products():
    products = await retrieve_products()
    if products:
        return ResponseModel(products, "products data retrieved successfully")
    return ResponseModel(products, "Empty list returned")


@router.get("/{id}", response_description="product data retrieved")
async def get_product_data(id):
    product = await retrieve_product(id)
    if product:
        return ResponseModel(product, "product data retrieved successfully")
    return ErrorResponseModel("An error occurred.", 404, "product doesn't exist.")


@router.put("/{id}")
async def update_product_data(id: str, req: UpdateProductModel = Body(...)):
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


@router.delete("/{id}", response_description="product data deleted from the database")
async def delete_product_data(id: str):
    deleted_product = await delete_product(id)
    if deleted_product:
        return ResponseModel(
            "product with ID: {} removed".format(id), "product deleted successfully"
        )
    return ErrorResponseModel(
        "An error occurred", 404, "product with id {0} doesn't exist".format(id)
    )
