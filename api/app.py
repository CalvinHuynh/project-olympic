from api.app_setup import create_app
from api.jobs import bg_scheduler

app = create_app()
bg_scheduler.start()

if __name__ == "__main__":
    app.run()
