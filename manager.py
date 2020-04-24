from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from Application import _Config
from Application.models import db
from Application import Mouthful

app = Mouthful
app.config.from_object(_Config.DEV)
db.init_app(app)
migrate = Migrate(app, db, compare_type=True)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
