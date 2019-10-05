import logging.config

logging.config.fileConfig('logging.conf')
logging.info("something happens")
logging.warning("something else")
