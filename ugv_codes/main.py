
from app.conf_interface import conf_interface
from app.cache import update_cache
from app.rtmp import run_rtmp
from config import Config

name, password = conf_interface()
update_cache({"name": name, "password": password})

# run_rtmp(f"{Config.RTMP_URL}/{name}")
