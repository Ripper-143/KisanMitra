from datetime import datetime
from sqlalchemy import String, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.database import Base


class Farmer(Base):
    __tablename__ = "farmers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[str] = mapped_column(String, default="", nullable=True)
    phone_number: Mapped[str] = mapped_column(String, default="", nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    land_profiles: Mapped[list["LandProfile"]] = relationship("LandProfile", back_populates="farmer", cascade="all, delete-orphan")
    alert_logs: Mapped[list["AlertLog"]] = relationship("AlertLog", back_populates="farmer", cascade="all, delete-orphan")
    crop_diagnoses: Mapped[list["CropDiagnosis"]] = relationship("CropDiagnosis", back_populates="farmer", cascade="all, delete-orphan")


class LandProfile(Base):
    __tablename__ = "land_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    farmer_id: Mapped[int] = mapped_column(Integer, ForeignKey("farmers.id", ondelete="CASCADE"), nullable=False)
    state: Mapped[str] = mapped_column(String, nullable=False)  # Andhra Pradesh or Telangana
    district: Mapped[str] = mapped_column(String, nullable=False)
    village: Mapped[str] = mapped_column(String, nullable=False)
    crop_type: Mapped[str] = mapped_column(String, nullable=False)  # Cotton, Paddy, Maize, Red Chilli, Turmeric
    land_size_acres: Mapped[float] = mapped_column(Float, nullable=False)
    soil_type: Mapped[str] = mapped_column(String, nullable=False)  # Black Soil, Red Soil, Sandy, Loam
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    farmer: Mapped["Farmer"] = relationship("Farmer", back_populates="land_profiles")


class AlertLog(Base):
    __tablename__ = "alert_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    farmer_id: Mapped[int] = mapped_column(Integer, ForeignKey("farmers.id", ondelete="CASCADE"), nullable=False)
    alert_type: Mapped[str] = mapped_column(String, nullable=False)  # Weather, Market Price, Scheme, System
    message: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, default="Sent", nullable=False)  # Sent, Simulated, Failed
    sent_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    farmer: Mapped["Farmer"] = relationship("Farmer", back_populates="alert_logs")


class CropDiagnosis(Base):
    __tablename__ = "crop_diagnoses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    farmer_id: Mapped[int] = mapped_column(Integer, ForeignKey("farmers.id", ondelete="CASCADE"), nullable=False)
    crop_type: Mapped[str] = mapped_column(String, nullable=False)
    disease_detected: Mapped[str] = mapped_column(String, nullable=False)
    severity: Mapped[str] = mapped_column(String, nullable=False)
    diagnosis_details: Mapped[str] = mapped_column(String, nullable=False)
    image_path: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    farmer: Mapped["Farmer"] = relationship("Farmer", back_populates="crop_diagnoses")
