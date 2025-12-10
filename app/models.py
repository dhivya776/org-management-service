from pydantic import BaseModel, EmailStr

# --- Request Models (Input) ---
class OrgCreateRequest(BaseModel):
    organization_name: str
    email: EmailStr
    password: str

class OrgUpdateRequest(BaseModel):
    organization_name: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# --- Response/DB Models ---
class Token(BaseModel):
    access_token: str
    token_type: str
    org: str