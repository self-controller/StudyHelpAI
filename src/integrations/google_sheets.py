from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


from src.prompts.prompts import messages
from src.models.lecture_models import SubTopic, Assignment, DocNotes

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

CREDS_DIR = Path("data/credentials")
CREDS_PATH = CREDS_DIR / "credentials.json"
TOKEN_PATH = CREDS_DIR / "token.json"

CREDS_DIR.mkdir(parents=True, exist_ok=True)

class GoogleSheetsClient:
    def __init__(self):
        self.creds = None
        if TOKEN_PATH.exists():
            self.creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(str(CREDS_PATH), SCOPES)
                self.creds = flow.run_local_server(port=0)
            CREDS_DIR.mkdir(parents=True, exist_ok=True)
            with open(TOKEN_PATH, "w") as token:
                token.write(self.creds.to_json())
        self.service = build("sheets", "v4", credentials=self.creds)
    
    def write_data(self, spreadsheet_id: str, range_name: str, values: list) -> None:
        request = self.service.spreadsheets().values().append(
            spreadsheet_id=spreadsheet_id,
            range=range_name,
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body = {'values': values}
        )
        response = request.execute()
        print(f"Data written to {spreadsheet_id} at range {range_name}")
        return response
    def create_spreadsheet(self, title: str) -> str:
        body = {
            'properties': {'title': title}
        }
        spreadsheet = self.service.spreadsheets().create(body=body).execute()
        return spreadsheet['spreadsheetId']