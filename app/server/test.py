def basket_helper(basket) -> dict:
    return {
        "id": str(basket["_id"]),
        "fullname": basket["fullname"],
        "email": basket["email"],
        "course_of_study": basket["course_of_study"],
        "year": basket["year"],
        "GPA": basket["gpa"],
    }

# Retrieve all baskets present in the database

async def retrieve_baskets():
    baskets = []
    async for basket in basket_collection.find():
        baskets.append(basket_helper(basket))
    return baskets


# Add a new basket into to the database
async def add_basket(basket_data: dict) -> dict:
    basket = await basket_collection.insert_one(basket_data)
    new_basket = await basket_collection.find_one({"_id": basket.inserted_id})
    return basket_helper(new_basket)


# Retrieve a basket with a matching ID
async def retrieve_basket(id: str) -> dict:
    basket = await basket_collection.find_one({"_id": ObjectId(id)})
    if basket:
        return basket_helper(basket)


# Update a basket with a matching ID
async def update_basket(id: str, data: dict):
    # Return false if an empty request body is sent.
    if len(data) < 1:
        return False
    basket = await basket_collection.find_one({"_id": ObjectId(id)})
    if basket:
        updated_basket = await basket_collection.update_one(
            {"_id": ObjectId(id)}, {"$set": data}
        )
        if updated_basket:
            return True
        return False


# Delete a basket from the database
async def delete_basket(id: str):
    basket = await basket_collection.find_one({"_id": ObjectId(id)})
    if basket:
        await basket_collection.delete_one({"_id": ObjectId(id)})
        return True
