SERVER_CREDENTIALS_SCHEMA = {
    "type": "dict",
    "keys": {
        "api_url": {
            "type": "string",
            "title": "API URL (3X-UI)",
            "required": True,
            "help": "Пример: http://1.2.3.4:2053",
        },
        "username": {
            "type": "string",
            "title": "Логин",
            "required": True,
        },
        "password": {
            "type": "string",
            "title": "Пароль",
            "required": True,
        },
    },
}
