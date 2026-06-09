import string
import random
from sqlalchemy.orm import Session
from app.repositories.clinic_repository import clinic_repository
from app.schemas.clinic import ClinicCreate, ClinicUpdate, ClinicStatusUpdate
from app.schemas.user import UserCreate
from app.services.user_service import user_service
from app.core.exceptions import NotFoundException, ConflictException
from app.utils.constants import CLINIC_ADMIN, CLINIC_ACTIVE

class ClinicService:
    @staticmethod
    def _generate_centre_code(db: Session) -> str:
        clinics = clinic_repository.get_multi(db, limit=10000)
        max_id = len(clinics)
        while True:
            max_id += 1
            code = f"CENT{max_id:03d}"
            if not clinic_repository.get_by_centre_code(db, code):
                return code

    @staticmethod
    def _generate_random_password(length=10):
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        return "".join(random.choice(chars) for _ in range(length))

    @staticmethod
    def create_clinic(db: Session, clinic_in: ClinicCreate, created_by: str = None):
        centre_code = ClinicService._generate_centre_code(db)
        
        clinic_data = clinic_in.model_dump()
        clinic_data["centre_code"] = centre_code
        clinic_data["status"] = CLINIC_ACTIVE
        if created_by:
            clinic_data["created_by"] = created_by
            
        clinic = clinic_repository.create_clinic(db, obj_in=clinic_data)

        username = f"admin_{centre_code.lower()}"
        password = ClinicService._generate_random_password()
        
        user_in = UserCreate(
            name=f"Admin {clinic.clinic_name}",
            username=username,
            password=password,
            role=CLINIC_ADMIN
        )
        
        user = user_service.create_user(db, centre_code, user_in, created_by)
        
        return clinic, username, password

    @staticmethod
    def get_clinic(db: Session, clinic_id: str):
        clinic = clinic_repository.get(db, id=clinic_id)
        if not clinic:
            raise NotFoundException("Clinic not found")
        return clinic

    @staticmethod
    def get_clinics(db: Session, skip: int = 0, limit: int = 100):
        return clinic_repository.get_multi(db, skip=skip, limit=limit)

    @staticmethod
    def update_clinic(db: Session, clinic_id: str, clinic_in: ClinicUpdate, updated_by: str = None):
        clinic = ClinicService.get_clinic(db, clinic_id)
        update_data = clinic_in.model_dump(exclude_unset=True)
        if updated_by:
            update_data["updated_by"] = updated_by
        return clinic_repository.update(db, db_obj=clinic, obj_in=update_data)

    @staticmethod
    def update_status(db: Session, clinic_id: str, status_in: ClinicStatusUpdate, updated_by: str = None):
        clinic = ClinicService.get_clinic(db, clinic_id)
        return clinic_repository.update(db, db_obj=clinic, obj_in={"status": status_in.status, "updated_by": updated_by})

clinic_service = ClinicService()
