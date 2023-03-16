class config:
    ADMIN_EMAIL='test@memba.com'
    SECRET_KEY='4A)1D710k'

class LiveConfig(config):
    ADMIN_EMAIL='admin@memba.com'
    SERVER_ADDRESS='https://server.memba.com'

class TestConfig(config):
    SERVER_ADDRESS='https://127.0.0.1:5000'

