"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows, Likes

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def Test_Message_Model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        m = Message(
            text="testtext"
        )

        db.session.add(m)
        m.user.append(u)
        db.session.commit()

        self.assertEqual(len(m.user), 1)
        self.assertEqual(len(m.likes), 0)

    def Test_Message_Method_repr_(self):
        """Does message __repr__ method work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        m2 = Message(
            text="testmessage"
        )

        db.session.add(m2)
        m2.user.append(u)
        db.session.commit()


        self.assertIs(m2.__repr__(), "<Message #2: User ID- 1, testmessage>")

    def Test_Message_Like_Feature(self):
        """Does Message Likes work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        m = Message(
            text="testmessage"
        )

        db.session.add(u)
        db.session.add(m)
        db.session.commit()
        
        u.likes.append(m)
        db.session.commit()

        self.assertEqual(len(u.likes), 1)
        