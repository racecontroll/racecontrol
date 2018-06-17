from ...util.framework.blueprint import create_blueprint

blueprint = create_blueprint("driver", __name__)

from . import views
