from dotenv import load_dotenv

load_dotenv()

prop = {
    'traffic': {
        "api_key": 'TRAFFIC_API_KEY',
        "base_url": 'TRAFFIC_API_BASE',
    },
    'cctv': {
        "api_key": 'CCTV_API_KEY',
        "base_url": 'CCTV_API_BASE',
    },
    'weather': {
        "api_key": 'WEATHER_API_KEY',
        "base_url": 'WEATHER_API_BASE',
    },
    'server': {
        "host": 'SERVER_HOST',
        "port": 'SERVER_PORT',
        "reload": 'SERVER_RELOAD',
    },
    'web': {
        "allow_origins": ['*'],
        "token": 'API_TOKEN',
    },
}
