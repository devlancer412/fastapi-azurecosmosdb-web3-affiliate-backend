## Do not edit
__author__ = "ZiYi Tung"
__copyright__ = "Copyright 2022, Metadhana Studio"
__license__ = "INTERNAL"
__version__ = "0.1.8"
__maintainer__ = __author__
__email__ = "zi@metadhana.io"
__status__ = "alpha"


from fastapi import FastAPI
from app.__internal import bootstrap

app = FastAPI(
    title="Affiliate API",
    description="Affiliate marketing backend API",
    version="-".join([__version__, __status__]),
)

bootstrap(app)
