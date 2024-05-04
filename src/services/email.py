from src.classes.gmail.email_message import EmailMessage, MessageListItem
from src.services.gmail_api import GmailService
from src.utils.list_utils import transform

class EmailService:

  def __init__(self, gmailService: GmailService) -> None:
    self.gmail = gmailService

  @property
  def baseUrl(self):
    return self.gmail.service.users()

  def getProfile(self, userId: str):
    return self.baseUrl(userId=userId).execute()

  def getMessages(self, userId: str) -> list[EmailMessage]:
    msgPath = self.baseUrl.messages()

    messageList = [ MessageListItem(**msg) for msg in msgPath.list(userId=userId).execute().get('messages') ]

    return transform(messageList, lambda msg: msg.getDetails(msgPath, userId))
