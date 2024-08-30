from bot import main
from main import app
import uvicorn
import threading


def start_api():
    uvicorn.run(app, host='0.0.0.0', port=8000)


def start():
    api_task = threading.Thread(target=start_api)

    api_task.start()

    main()


start()
