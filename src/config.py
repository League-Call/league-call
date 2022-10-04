
from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix=False,
    settings_files=['settings.toml', '.secrets.toml'],
    load_dotenv=True,
)


assert settings.PROJECT_NAME == 'League Call'
