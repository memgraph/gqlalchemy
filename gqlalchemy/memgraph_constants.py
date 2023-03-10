import os

MG_HOST = os.getenv("MG_HOST", "127.0.0.1")
MG_PORT = int(os.getenv("MG_PORT", "7687"))
MG_USERNAME = os.getenv("MG_USERNAME", "")
MG_PASSWORD = os.getenv("MG_PASSWORD", "")
MG_ENCRYPTED = os.getenv("MG_ENCRYPT", "false").lower() == "true"
MG_CLIENT_NAME = os.getenv("MG_CLIENT_NAME", "GQLAlchemy")
MG_LAZY = os.getenv("MG_LAZY", "false").lower() == "true"
