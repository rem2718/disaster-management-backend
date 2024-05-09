from conf_interface import conf_interface
from cache import update_cache
from rtmp import run_rtmp
from config import Config

name, password = conf_interface()
update_cache({"name": name, "password": password})

# run_rtmp(f"{Config.RTMP_URL}/{name}")
