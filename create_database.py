import os
from app import create_app


basedir = os.path.abspath(os.path.dirname(__file__))

if __name__ == '__main__':
    flask_app = create_app(os.environ.get('APP_CONFIG', 'default'))

    with flask_app.test_request_context():
        from app.models import User, Book, db

        db.create_all()

        if len(User.query.all()) == 0:
            admin = User(
                client_id='rastadev',
                secret='rastadev'
            )
            db.session.add(admin)
            db.session.commit()
            print('admin created')
