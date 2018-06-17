from ...util.framework.blueprint import create_blueprint

blueprint = create_blueprint("car", __name__)

from . import views
