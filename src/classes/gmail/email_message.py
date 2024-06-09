from dataclasses import dataclass, field
import re
from typing import Any
from markdownify import markdownify as md
from src.interfaces.gmail import MessageHeader, MessagePart
from src.utils.list_utils import findFirst, transform
import base64
import datetime
from bs4 import BeautifulSoup
from src.utils.string_util import stringCleanUp
from pdfkit import from_string
from pdf2image import convert_from_path
import mimetypes
import logging

emailFetcherLogger = logging.getLogger('Email')
allowedType = ["image/jpeg", "image/jpg", "image/png"]

mimetypes.init()

def getHtmlBodyContents(htmlStr: str):
  html = BeautifulSoup(htmlStr, 'html.parser')

  # promotional emails use a "<body> n x <table> structure"
  # we should start by pulling out the table cells
  tableCells = html.findAll('td')
  # tableCells = filter(lambda elem: not elem.get('is_empty_element', False), list(tableCells))

  # tableCells = [ [cell, md(cell, heading_style="ATX")] for cell in tableCells ]

  tableCells = [
    stringCleanUp(
      rawHtmlStr.text,
      [
        [r'\n{3,}', '\n\n'],      # Remove excessive new lines
        [r'â', '-'],              # Remove unicode character
        [r'', ''],               # Remove unicode character
        [r'\x94', '', re.UNICODE] # Remove unicode character
      ]
    )
    for rawHtmlStr
    in tableCells
  ]

  print(tableCells)

@dataclass(kw_only=True)
class MessageListItem:
  """Representation of a single 'message' in the Google API List Response"""
  id: str
  threadId: str

  def getDetails(self, messagePath, userId):
    return EmailMessage.fromGoogleAPI(messagePath.get(userId=userId, id=self.id).execute())

@dataclass()
class EmailMessage(MessageListItem):
  id: str
  subject: str
  recipient: str
  sender: str
  replyTo: str
  date: str
  text: str
  pdf: str
  pdfData: bytes
  html: str
  images: list[str]
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

    print(f'> Loading Email {message.get("id")}')

    payload: MessagePart = message.get('payload')
    headers: list[MessageHeader] = payload.get('headers', [])

    print(f'  > Getting HTML Content')
    htmlContent = getBody('text/html', payload)
    # getHtmlBodyContents(htmlContent)

    print(f'  > Creating PDF')
    htmlPdf = ''
    pdfPath = ''
    encodedPDF = bytes()
    try:
      htmlPdf = from_string(htmlContent)
      pdfPath = f'./var/email-{message.get("id")}.pdf'

      encodedPDF = base64.urlsafe_b64encode(htmlPdf)

      with open(pdfPath, 'wb') as f:
        f.write(htmlPdf)
    except:
      print(f'     Error creating PDF from HTML')
      emailFetcherLogger.warn(f'Unable to convert html to pdf: {message.get("id")}')


    imageFiles = []
    if (pdfPath):
      print(f'  > Creating Images')
      pdfImages = convert_from_path(pdfPath, fmt='png', dpi=800)
      
      for idx,page in enumerate(pdfImages):
        pageFilename = f'./var/email-{message.get("id")}-page-{idx}.png'
        imageFiles.append(pageFilename)
        page.save(pageFilename)

    print(f'  > Creating Text Content')
    textContent = getBody('text/plain', payload) or md(str(htmlContent), heading_style="ATX")

    print(f'  > Loaded Email [id: {message.get("id")}] - {getHeader("subject", headers)}')

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
      pdf=pdfPath,
      pdfData=encodedPDF,
      images=imageFiles,
      text=textContent,
      labels=message.get('labelIds', [])
    )
