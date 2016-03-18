import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/catalogApp/catalog/")
from application import app as application
application.secret_key = 'now_for_something_completely_different'
