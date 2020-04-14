from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from Application import _Config, models
from Application.models import db

from Application import create_app
# TODO test manager
app = create_app()
app.config.from_object(_Config.dbconf)
db.init_app(app)
migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
