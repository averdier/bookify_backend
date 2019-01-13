import os
from app import create_app


basedir = os.path.abspath(os.path.dirname(__file__))

if __name__ == '__main__':
    flask_app = create_app(os.environ.get('APP_CONFIG', 'default'))

    with flask_app.test_request_context():
        from app.models import Client, Book, BookOffer

        Client.init()
        Book.init()
        BookOffer.init()

        response = Client.search().execute()
        if Client.search().execute().hits.total == 0:
            admin = Client(
                client_id='rastadev',
                secret='rastadev',
                email='a.verdier@outlook.fr',
                confirmed=True,
                favorite_genders=['chill', 'science'],
                balance=999999999
            )
            admin.save()
            print('admin created')
