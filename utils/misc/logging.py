import logging

INFO = logging.INFO
logging.root.setLevel(INFO)

logging.basicConfig(
    format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
    level=INFO
)

DATABASE_LOGS_HANDLER = logging.StreamHandler()
DATABASE_LOGGER = logging.Logger("Database")
DATABASE_LOGGER.addHandler(DATABASE_LOGS_HANDLER)

