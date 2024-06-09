import logging
import os
import logging.handlers
import logging.config
import src.config

defaultConfig = {
   'version': 1,
   'disable_existing_loggers': False,
   'formatters': {},
   'handlers': {
      'stdout': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://sys.stdout',
        'level': 'INFO'
      },
      'stderr': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://sys.stderr',
        'level': 'WARNING',
        'filters': ['error']
      }
   },
   'filters': {
      'error': {
         '()': 'src.logging.ErrorFilter'
      }
   },
   'loggers': {
      'app': {
        'propagate': True
      }
   },
   'root': {
      'handlers': ['stdout', 'stderr']
   }
}

class ErrorFilter(logging.Filter):
    def filter(self, record):
      return record.levelno > logging.WARNING

if (not os.path.isdir('./logs')):
  os.mkdir('logs')

file_handler = logging.handlers.RotatingFileHandler(
  filename="./logs/dnd-ai-api.log",
  backupCount=3
)

console_handler = logging.StreamHandler()

logging.basicConfig(
  level=logging.INFO,
  format='%(asctime)s [%(levelname)s] %(name)s - %(message)s',
  handlers=[]
)

def initializeLogger():
  # config = src.config.getConfig('Logging')
  config = defaultConfig
  logging.config.dictConfig(config)