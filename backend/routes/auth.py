from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from auth import create_access_token, get_password_hash, verify_password, get_current_user
from models.database import get_db
from models.models import Farmer, LandProfile

router = APIRouter(prefix="/auth", tags=["Auth"])

# ── Pydantic Request/Response Models ──────────────────────────────────────────

class LandProfileSchema(BaseModel):
    state: str
    district: str
    village: str
    crop_type: str
    land_size_acres: float
    soil_type: str

class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone_number: str
    land_profile: LandProfileSchema

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    email: str
    full_name: str
    phone_number: str
    land_profile: dict

# ── Routes ───────────────────────────────────────────────────────────────────

@router.post("/signup", response_model=TokenResponse, status_code=201)
def signup(body: SignupRequest, db: Session = Depends(get_db)):
    """Registers a new farmer, sets up their land profile, and returns a JWT."""
    existing = db.query(Farmer).filter(Farmer.email == body.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    # Create farmer
    farmer = Farmer(
        email=body.email,
        hashed_password=get_password_hash(body.password),
        full_name=body.full_name,
        phone_number=body.phone_number
    )
    db.add(farmer)
    db.commit()
    db.refresh(farmer)

    # Create land profile for farmer
    land = LandProfile(
        farmer_id=farmer.id,
        state=body.land_profile.state,
        district=body.land_profile.district,
        village=body.land_profile.village,
        crop_type=body.land_profile.crop_type,
        land_size_acres=body.land_profile.land_size_acres,
        soil_type=body.land_profile.soil_type
    )
    db.add(land)
    db.commit()
    db.refresh(land)

    # Generate token
    token = create_access_token({"sub": str(farmer.id)})
    
    return TokenResponse(
        access_token=token,
        user_id=farmer.id,
        email=farmer.email,
        full_name=farmer.full_name,
        phone_number=farmer.phone_number,
        land_profile={
            "id": land.id,
            "state": land.state,
            "district": land.district,
            "village": land.village,
            "crop_type": land.crop_type,
            "land_size_acres": land.land_size_acres,
            "soil_type": land.soil_type
        }
    )

@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    """Authenticates farmer and returns JWT along with profile information."""
    farmer = db.query(Farmer).filter(Farmer.email == body.email).first()
    if not farmer or not verify_password(body.password, farmer.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    # Get land profile
    land = db.query(LandProfile).filter(LandProfile.farmer_id == farmer.id).first()
    land_data = {}
    if land:
        land_data = {
            "id": land.id,
            "state": land.state,
            "district": land.district,
            "village": land.village,
            "crop_type": land.crop_type,
            "land_size_acres": land.land_size_acres,
            "soil_type": land.soil_type
        }

    token = create_access_token({"sub": str(farmer.id)})
    return TokenResponse(
        access_token=token,
        user_id=farmer.id,
        email=farmer.email,
        full_name=farmer.full_name or "",
        phone_number=farmer.phone_number or "",
        land_profile=land_data
    )

@router.get("/me")
def get_me(current_user: Farmer = Depends(get_current_user), db: Session = Depends(get_db)):
    """Fetch current user details."""
    land = db.query(LandProfile).filter(LandProfile.farmer_id == current_user.id).first()
    land_data = {}
    if land:
        land_data = {
            "id": land.id,
            "state": land.state,
            "district": land.district,
            "village": land.village,
            "crop_type": land.crop_type,
            "land_size_acres": land.land_size_acres,
            "soil_type": land.soil_type
        }
    return {
        "user_id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "phone_number": current_user.phone_number,
        "land_profile": land_data
    }
