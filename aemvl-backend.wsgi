#!/opt/miniconda3/envs/aemvl-backend/bin/python
import site
site.addsitedir('/opt/miniconda3/envs/aemvl-backend/lib/python3.5/site-packages')

import sys
sys.path.insert(0, '/var/www/aemvl-backend')

from main import app as application
