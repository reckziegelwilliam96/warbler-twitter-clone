"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

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

    def Test_User_Model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def Test_User_Method_repr_(self):
        """Does user __repr__ method work?"""

        u2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )

        db.session.add(u2)
        db.session.commit()


        self.assertIs(u2.__repr__(), "<User #2: testuser2, test2@test.com>")

    def Test_User_Method_Follows(self):
        """Does following method work"""

        u1 = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        u2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )
        db.session.add(u1)
        db.session.add(u2)

        u1.following.append(u2)
        
        db.session.commit()

        self.assertTrue(u1.is_following(u2))
        self.assertTrue(u2.is_followed_by(u1))

        self.assertFalse(u2.is_following(u1))
        self.assertFalse(u1.is_followed_by(u2))

    def Test_User_Method_Sign_Up(self):
        """Does user sign up method work?"""

        u1 = User.signup(
            username="testuser",
            email="test@test.com",
            password="testpassword",
            image_url = User.image_url.default
        )

        u2 = User.signup(
            username="testuser",
            email="test@test.com",
            password="testpassword",
            image_url = User.image_url.default
        )

        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        self.assertIsInstance(u1, User)
        self.assertIsNotInstance(u2, User)

    def Test_User_Method_Authenticate(self):
        """Does user authenticate method work?"""

        u1 = User.signup(
            username="testuser",
            email="test@test.com",
            password="testpassword"
        )

        db.session.add(u1)
        db.session.commit()

        user = User.authenticate(u1.username, u1.password)
        user2 = User.authenticate("testuser2", u1.password)
        user3 = User.authenticate(u1.username, "testpassword2")

        self.assertTrue(user)
        self.assertFalse(user2)
        self.assertFalse(user3)
