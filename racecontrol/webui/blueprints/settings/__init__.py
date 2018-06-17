from ...util.framework.blueprint import create_blueprint

blueprint = create_blueprint("settings", __name__)

from . import views
