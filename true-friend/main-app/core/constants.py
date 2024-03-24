import os

generation_app_name = os.environ.get("GENERATION_APP_NAME")
generation_app_port = os.environ.get("GENERATION_APP_PORT")
generation_app_url = f"http://{generation_app_name}:{generation_app_port}"