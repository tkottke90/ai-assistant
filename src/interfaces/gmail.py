from typing import TypedDict

MessageHeader = TypedDict('MessageHeader', { 'name': str, 'value': str })
MessageBody = TypedDict('MessageBody', {
  'size': str,
  'attachmentId': int,
  'data': str
})
MessagePart = TypedDict('MessagePart', {
  'partId': str,
  'mimeType': str,
  'filename': str,
  'headers': list[MessageHeader],
  'body': MessageBody,
  'parts': list
})