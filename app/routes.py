# app/routes.py
from fastapi import APIRouter, HTTPException, Depends
from app.models import OrgCreateRequest, OrgUpdateRequest, LoginRequest, Token
from app.database import db
from app.auth import get_password_hash, verify_password, create_access_token, decode_token

router = APIRouter()

# 1. Create Organization
@router.post("/org/create")
async def create_org(request: OrgCreateRequest):
    # Check duplicate org
    if await db.org_collection.find_one({"name": request.organization_name}):
        raise HTTPException(status_code=400, detail="Organization already exists")
    
    # Generate dynamic collection name
    _, coll_name = await db.get_dynamic_collection(request.organization_name)

    # Create Admin User
    user_doc = {
        "email": request.email,
        "password": get_password_hash(request.password),
        "organization": request.organization_name,
        "role": "admin"
    }
    await db.users_collection.insert_one(user_doc)

    # Save Metadata
    org_doc = {
        "name": request.organization_name,
        "admin_email": request.email,
        "collection_name": coll_name
    }
    await db.org_collection.insert_one(org_doc)

    # --- FIX START: Convert ObjectId to string for JSON compatibility ---
    org_doc["_id"] = str(org_doc["_id"])
    # --- FIX END ---

    # Initialize dynamic collection
    await db.master_db[coll_name].insert_one({"info": "Organization Initialized"})

    return {"message": "Organization created successfully", "data": org_doc}

# 2. Get Organization
@router.get("/org/get")
async def get_org(organization_name: str):
    # We use {"_id": 0} here to exclude the ID field entirely, preventing errors
    org = await db.org_collection.find_one({"name": organization_name}, {"_id": 0})
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org

# 3. Update Organization
@router.put("/org/update")
async def update_org(request: OrgUpdateRequest):
    # Verify Admin
    user = await db.users_collection.find_one({"email": request.email})
    if not user or not verify_password(request.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    old_name = user["organization"]
    new_name = request.organization_name

    # Check if new name is taken
    if await db.org_collection.find_one({"name": new_name}):
        raise HTTPException(status_code=400, detail="New name already exists")

    # Get Collections
    old_coll, _ = await db.get_dynamic_collection(old_name)
    new_coll, new_coll_name = await db.get_dynamic_collection(new_name)

    # Sync Data: Copy docs from old to new
    docs = await old_coll.find({}).to_list(length=None)
    if docs:
        await new_coll.insert_many(docs)
    
    # Update Metadata
    await db.org_collection.update_one({"name": old_name}, {"$set": {"name": new_name, "collection_name": new_coll_name}})
    await db.users_collection.update_one({"email": request.email}, {"$set": {"organization": new_name}})
    
    # Delete old collection
    await old_coll.drop()

    return {"message": "Organization updated and data synced."}

# 4. Delete Organization (Protected)
@router.delete("/org/delete")
async def delete_org(organization_name: str, token: dict = Depends(decode_token)):
    if token["org"] != organization_name:
        raise HTTPException(status_code=403, detail="Unauthorized action")

    await db.org_collection.delete_one({"name": organization_name})
    await db.users_collection.delete_many({"organization": organization_name})
    
    coll, _ = await db.get_dynamic_collection(organization_name)
    await coll.drop()

    return {"message": "Organization deleted"}

# 5. Admin Login
@router.post("/admin/login", response_model=Token)
async def login(request: LoginRequest):
    user = await db.users_collection.find_one({"email": request.email})
    if not user or not verify_password(request.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"sub": user["email"], "org": user["organization"]})
    return {"access_token": token, "token_type": "bearer", "org": user["organization"]}