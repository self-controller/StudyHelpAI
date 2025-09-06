import os  
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


SCOPES = ["https://www.googleapis.com/auth/documents"]

CREDS_DIR = Path("data/credentials")
CREDS_PATH = CREDS_DIR / "credentials.json"
TOKEN_PATH = CREDS_DIR / "token.json"

class GoogleDocsClient:
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
            with open(TOKEN_PATH, "w") as token:
                token.write(self.creds.to_json())
        self.service = build("docs", "v1", credentials=self.creds)

    def get_document(self, document_id):
        return self.service.documents().get(documentId=document_id).execute()

    def extract_text(self, document):
        text = ""
        for element in document.get("body", {}).get("content", []):
            if "paragraph" in element:
                for para_element in element["paragraph"].get("elements", []):
                    if "textRun" in para_element:
                        text += para_element["textRun"].get("content", "")
        return text
    
    def create_doc(self, title: str) -> str: 
        body = {"title": title}
        doc = self.service.documents().create(body=body).execute()
        return doc["documentId"]

    def write_text(self, document_id: str, text: str) -> None:
        requests = [
            {
                "insertText": {
                    "location": {"index": 1},
                    "text": text
                }
            }
        ]
        self.service.documents().batchUpdate(documentId=document_id, body={"requests": requests}).execute()