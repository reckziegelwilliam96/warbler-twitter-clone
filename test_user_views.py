"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

    def Test_Logged_In_User_Card_Home(self):
        """Can get user on home page?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

                response = self.client.get('/')
                self.assertIn({self.testuser.id}, response.data)
                self.assertIn({self.testuser.image_url}, response.data)
                self.assertIn(b'Messages', response.data)
                self.assertIn(b'Following', response.data)
                self.assertIn(b'Followers', response.data)

    def Test_Logged_Out_User_Card_Home(self):

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = not self.testuser.id

                response = self.client.get('/')
                self.assertIn({self.testuser.id}, response.data)
                self.assertIn({self.testuser.image_url}, response.data)
                self.assertIn(b'Messages', response.data)
                self.assertIn(b'Following', response.data)
                self.assertIn(b'Followers', response.data)
                