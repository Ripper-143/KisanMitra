import os
import sys
import unittest
from fastapi.testclient import TestClient

# Adjust path to find modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import app
from models.database import engine, Base
from rag.chroma_client import RAGDatabase

class TestKisanMitra(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create database tables
        Base.metadata.create_all(bind=engine)
        
        # Initialize RAG Database and ingest sample guidelines
        print("Preloading ChromaDB for unit test verification...")
        db = RAGDatabase()
        db.reset_database()
        
        # Verify ingestion works
        from rag.ingest import run_ingestion
        run_ingestion()
        
        cls.client = TestClient(app)
        cls.token = ""

    def test_01_health(self):
        """Verify health check returns ok."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "healthy")

    def test_02_auth_flow(self):
        """Verify registration and login flow works correctly."""
        # Cleanup potential previous test user
        # (Using a fresh email format to avoid unique constraint issues)
        email = f"test_farmer_{os.urandom(4).hex()}@kisanmitra.org"
        signup_payload = {
            "email": email,
            "password": "strongpassword123",
            "full_name": "Test Farmer AP",
            "phone_number": "+919876543210",
            "land_profile": {
                "state": "Andhra Pradesh",
                "district": "Guntur",
                "village": "Amaravati",
                "crop_type": "Cotton",
                "land_size_acres": 3.5,
                "soil_type": "Black Cotton Soil"
            }
        }
        
        # 1. Sign up
        response = self.client.post("/auth/signup", json=signup_payload)
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["full_name"], "Test Farmer AP")
        self.assertEqual(data["land_profile"]["district"], "Guntur")
        
        # Save token for subsequent requests
        self.__class__.token = data["access_token"]
        
        # 2. Login
        login_payload = {
            "email": email,
            "password": "strongpassword123"
        }
        response = self.client.post("/auth/login", json=login_payload)
        self.assertEqual(response.status_code, 200)
        login_data = response.json()
        self.assertIn("access_token", login_data)

    def test_03_protected_weather(self):
        """Verify weather advisory endpoint is protected and returns advisories."""
        headers = {"Authorization": f"Bearer {self.__class__.token}"}
        response = self.client.get("/weather/advisory?city=Guntur", headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["city"], "Guntur")
        self.assertTrue(len(data["forecast"]) > 0)
        self.assertIn("spraying_suitability", data["forecast"][0])

    def test_04_protected_market(self):
        """Verify market price trends endpoint returns valid mandi lists."""
        headers = {"Authorization": f"Bearer {self.__class__.token}"}
        response = self.client.get("/market/prices?crop=Cotton&state=Andhra+Pradesh", headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(len(data["prices"]) > 0)
        self.assertEqual(data["prices"][0]["crop"], "Cotton")

    def test_05_protected_schemes_rag(self):
        """Verify scheme matching triggers ChromaDB RAG and matches templates."""
        headers = {"Authorization": f"Bearer {self.__class__.token}"}
        response = self.client.get("/schemes/match", headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(len(data["matched_schemes"]) > 0)
        # Verify YSR Rythu Bharosa is matched for Andhra Pradesh user
        names = [s["name"] for s in data["matched_schemes"]]
        self.assertIn("YSR Rythu Bharosa", names)
        self.assertIn("PM-KISAN", names)
        # Verify RAG context is populated
        self.assertTrue(len(data["rag_evidence"]) > 0)

    def test_06_protected_alerts(self):
        """Verify alerts dispatcher saves logs to database."""
        headers = {"Authorization": f"Bearer {self.__class__.token}"}
        
        # 1. Dispatch custom alert
        alert_payload = {
            "alert_type": "Weather",
            "message": "Storm alert: Seek safety in secure shelters."
        }
        response = self.client.post("/alerts/send", json=alert_payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        
        # 2. Get alerts list
        response = self.client.get("/alerts", headers=headers)
        self.assertEqual(response.status_code, 200)
        logs = response.json()
        self.assertTrue(len(logs) > 0)
        self.assertEqual(logs[0]["alert_type"], "Weather")
        self.assertEqual(logs[0]["message"], "Storm alert: Seek safety in secure shelters.")

    def test_07_all_india_mandis(self):
        """Verify mandi prices support all states and crops dynamically."""
        headers = {"Authorization": f"Bearer {self.__class__.token}"}
        
        # 1. Hardcoded state/crop (Punjab / Wheat)
        response = self.client.get("/market/prices?crop=Wheat&state=Punjab", headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(len(data["prices"]) > 0)
        self.assertEqual(data["prices"][0]["state"], "Punjab")
        self.assertEqual(data["prices"][0]["crop"], "Wheat")
        
        # 2. Dynamic state (Gujarat / Groundnut)
        response = self.client.get("/market/prices?crop=Groundnut&state=Gujarat", headers=headers)
        self.assertEqual(response.status_code, 200)
        data_dyn = response.json()
        self.assertTrue(len(data_dyn["prices"]) > 0)
        self.assertEqual(data_dyn["prices"][0]["state"], "Gujarat")
        self.assertEqual(data_dyn["prices"][0]["crop"], "Groundnut")

    def test_08_pdf_generation(self):
        """Verify crop diagnosis upload and ReportLab PDF streaming endpoint."""
        headers = {"Authorization": f"Bearer {self.__class__.token}"}
        
        # 1. Create a dummy leaf image file
        dummy_img_path = "test_leaf.jpg"
        from PIL import Image as PILImage
        img = PILImage.new('RGB', (100, 100), color = 'green')
        img.save(dummy_img_path)
        
        # 2. Perform mock upload
        try:
            with open(dummy_img_path, "rb") as f:
                response = self.client.post(
                    "/crop/diagnose",
                    files={"image": ("test_leaf.jpg", f, "image/jpeg")},
                    data={"crop_type": "cotton"},
                    headers=headers
                )
            self.assertEqual(response.status_code, 200)
            diag_data = response.json()
            self.assertIn("id", diag_data)
            diag_id = diag_data["id"]
            
            # 3. Request PDF download
            pdf_response = self.client.get(f"/crop/diagnose/{diag_id}/pdf", headers=headers)
            self.assertEqual(pdf_response.status_code, 200)
            self.assertEqual(pdf_response.headers["content-type"], "application/pdf")
            self.assertTrue(len(pdf_response.content) > 100) # Valid file bytes
        finally:
            if os.path.exists(dummy_img_path):
                os.remove(dummy_img_path)

if __name__ == "__main__":
    unittest.main()
