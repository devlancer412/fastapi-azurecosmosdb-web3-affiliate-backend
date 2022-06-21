## Do not edit
__author__ = "Von Villamor"
__copyright__ = "Copyright 2022, Metadhana Studio"
__license__ = "INTERNAL"
__version__ = "0.1.8"
__maintainer__ = __author__
__email__ = "von@metadhana.io"
__status__ = "alpha"


from fastapi import FastAPI
from .__internal import bootstrap

app = FastAPI(
    title="Generic API",
    description="Generic API description",
    version="-".join([__version__, __status__]),
)

bootstrap(app)
