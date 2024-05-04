from dataclasses import dataclass, field
from markdownify import markdownify as md
from src.interfaces.gmail import MessageHeader, MessagePart
from src.utils.list_utils import findFirst, transform
import base64
import datetime

@dataclass(kw_only=True)
class MessageListItem:
  """Representation of a single 'message' in the Google API List Response"""
  id: str
  threadId: str

  def getDetails(self, messagePath, userId):
    return EmailMessage.fromGoogleAPI(messagePath.get(userId=userId, id=self.id).execute())

@dataclass()
class EmailMessage(MessageListItem):
  subject: str
  recipient: str
  sender: str
  replyTo: str
  date: str
  text: str
  html: str
  unsubscribeUrl: str = field(default=str)
  labels: list[str] = field(default_factory=[])


  def fromGoogleAPI(message: dict):
    def getHeader(key: str, headerList: list[MessageHeader]):
      header = findFirst(
        headerList,
        lambda header: header.get('name', '').lower() == key
      )

      if (not header):
        return ''
      
      return header.get('value', '')
    
    def getBody(targetType: str, part: MessagePart):
      # If the mime type matches and the body has content, return it
      if (part.get('mimeType') == targetType and part.get('body').get('size') > 0):
        data = part.get('body').get('data', '')
        bytes = base64.urlsafe_b64decode(data)

        return bytes.decode('utf-8')
      
      if (len(part.get('parts', [])) > 0):
        children = transform(part.copy().get('parts'), lambda part: getBody(targetType, part))

        return findFirst(children, lambda body: body is not None)

      return None

    payload: MessagePart = message.get('payload')
    headers: list[MessageHeader] = payload.get('headers', [])

    htmlContent = getBody('text/html', payload)
    textContent = getBody('text/plain', payload) or md(str(htmlContent), heading_style="ATX")

    return EmailMessage(
      id=message.get('id'),
      threadId=message.get('threadId'),
      subject=getHeader('subject', headers),
      sender=getHeader('from', headers),
      recipient=getHeader('to', headers),
      replyTo=getHeader('reply-to', headers),
      unsubscribeUrl=getHeader('list-unsubscribe', headers),
      date=datetime.datetime.fromtimestamp(
        float(message.get('internalDate', 0)) / 1000.0
      ).strftime('%c'),
      html=htmlContent,
      text=textContent,
      labels=message.get('labelIds', [])
    )
