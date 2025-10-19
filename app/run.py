from app import create_app
from dotenv import load_dotenv
import socket


socket.getfqdn = lambda host=None: "localhost.localdomain"

load_dotenv("app/.env.dev")

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)


# from app import create_app

# app = create_app()

# if __name__ == '__main__':
#     app.run(port=8000, debug=True)
