from datetime import datetime
import os
import gspread
from gspread.spreadsheet import Spreadsheet
from typing import Dict, List, Tuple, TypedDict
from django.conf import settings
import firebase_admin
from firebase_admin import auth

def is_validate_google_token_id(token_id: str, user_id: str) -> bool:
    decoded_token = auth.verify_id_token(token_id)
    firebase_uid = decoded_token['uid']
    if firebase_uid != user_id:
        return False
    
    return True


#######################################
# ==== DELETE ALL THIS BELOW ====
#######################################
class GS_BoidSchema(TypedDict):
    user_id: int | str
    user_name: str
    date_joined: str
    color: str
    position_x: int | float
    position_y: int | float
    velocity_x: int | float
    velocity_y: int | float
    acceleration_x: int | float
    acceleration_y: int | float

    @staticmethod
    def validate(data: dict, soft: bool = False) -> dict:
        """Validates the input data against the schema."""
        errors = {}

        # Required fields and their expected types
        required_fields = {
            "user_id": (int, str),
            "user_name": str,
            "date_joined": str,
            "color": str,
            "position_x": (int, float),
            "position_y": (int, float),
            "velocity_x": (int, float),
            "velocity_y": (int, float),
            "acceleration_x": (int, float),
            "acceleration_y": (int, float),
        }

        for field, expected_types in required_fields.items():
            if field not in data and not soft:
                errors[field] = "This field is required."
            elif not isinstance(data[field], expected_types):
                errors[field] = f"Expected type {expected_types}, got {type(data[field]).__name__}."

        # Additional validation for date format
        # if "date_joined" in data:
        #     try:
        #         datetime.fromisoformat(data["date_joined"])
        #     except ValueError:
        #         errors["date_joined"] = "Invalid date format. Use ISO 8601 (e.g., 'YYYY-MM-DDTHH:MM:SS')."

        # Return errors if any
        if errors:
            raise ValueError(errors)

        return data


def initialize_gspread() -> gspread.client.Client:
    """
    Initialize a gspread client with the given credentials.
    """
    creds = get_credentials()
    return gspread.service_account_from_dict(
        creds
    )  # Note: we could move this to settings to do this once.


def get_credentials() -> dict:
    """
    Return gspread credentials.
    """
    return {
        "type": os.getenv("TYPE"),
        "project_id": os.getenv("PROJECT_ID"),
        "private_key_id": os.getenv("PRIVATE_KEY_ID"),
        "private_key": os.getenv("PRIVATE_KEY").replace("\\n", "\n"),
        "client_email": os.getenv("CLIENT_EMAIL"),
        "client_id": os.getenv("CLIENT_ID"),
        "auth_uri": os.getenv("AUTH_URI"),
        "token_uri": os.getenv("TOKEN_URI"),
        "auth_provider_x509_cert_url": os.getenv("AUTH_PROVIDER_X509_CERT_URL"),
        "client_x509_cert_url": os.getenv("CLIENT_X509_CERT_URL"),
        "universe_domain": os.getenv("UNIVERSE_DOMAIN"),
    }


class GSGenericORM:

    def __init__(self, doc_name: str, sheet_name: str = None, id_column: str = "id") -> None:
        self.spreadsheet: Spreadsheet = settings.GSPREAD_CLIENT.open(doc_name)
        self.worksheet = (
            self.spreadsheet.worksheet(sheet_name)
            if sheet_name
            else self.spreadsheet.get_worksheet(0)
        )
        self.headers = self.worksheet.row_values(
            1
        )
        self.id_column = id_column

    def all(self) -> List[GS_BoidSchema]:
        return self.worksheet.get_all_records()

    def insert(self, entry: GS_BoidSchema) -> Tuple[bool, str | None]:

        try:
            row = []
            for header in self.headers:
                row.append(entry.get(header))
        except KeyError as e:
            return False, f"Couldn't find header {header} in entry ({entry}): {e}"

        self.worksheet.append_row(row)
        return True, None
    
    def delete(self, record_id: str) -> Tuple[bool, str | None]:

        rows = self.all()
        
        for idx, row in enumerate(rows, start=2):
            if row.get(self.id_column, -1) == record_id:
                self.worksheet.delete_rows(idx)
                return True, None
                
        return False, "No entry in database"

    def update(self, record_id: str, updated_entry: Dict[str, str]) -> bool:
        rows = self.all()
        for idx, row in enumerate(rows, start=2):  # Start at 2 since the first row is headers
            if row.get(self.id_column, -1) == record_id:
                for key, value in updated_entry.items():
                    if key in self.headers:
                        col = self.headers.index(key) + 1
                        self.worksheet.update_cell(idx, col, value)
                return True
        return False

    def get_by_id(self, record_id: str) -> Tuple[bool, GS_BoidSchema | None]:
        rows = self.all()
        for row in rows:
            if int(row.get(self.id_column, -1)) == int(record_id):
                return True, row
        return False, None
