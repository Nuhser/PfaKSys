from PfaKSys import create_app
from PfaKSys.config.config import DevelopmentConfig


app = create_app(DevelopmentConfig)

if __name__ == '__main__':
    app.run(port=app.config['PORT'], use_reloader=app.config['USE_RELOADER'])
