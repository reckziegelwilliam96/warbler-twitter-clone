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


class MessageViewTestCase(TestCase):
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

    def Test_Logged_In_Add_Message(self):

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_csode, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")
    
    def Test_Logged_Out_Add_Message(self):
        """Can user add a message?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY]  =  not self.testuser.id


            resp = c.post("/messages/new", data={"text": "Hello"})

            self.assertEqual(resp.status_code, 404)

    def Test_Logged_In_Show_Message(self):
        """Can user see message on show page?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            result = c.post("/messages/new", data={"text": "Hello"})

            self.assertEqual(result.status_code, 302)

            resp = c.get(f"/messages/{self.testuser.id}")

            self.assertEqual(resp.status_code, 200)
            self.assertIn(result.data.message.text, "Hello")

    def Test_Logged_In_Delete_Message(self):

        with self.client as c:
            with c.session_transaction as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            result = c.post("/messages/new", data={"text": "Hello"})
            self.assertEqual(result.status_code, 302)

            resp = c.get(f"/messages/{self.testuser.id}")
            self.assertEqual(resp.status_code, 200)
            
            msg = Message.query.one()
            result2 = c.post(f"/messages/{self.testuser.id}/delete", data=msg)
            self.assertEqual(result2.status_code, 302)

            resp2 = c.get(f"/users/{self.testuser.id}")
            self.assertEqual(resp2.status_code, 200)
            self.assertFalse(msg)

    def Test_Logged_Out_Delete_Message(self):

        with self.client as c:
            with c.session_transaction as sess:
                sess[CURR_USER_KEY] =  self.testuser.id
                
                msg = Message(text="Hello")
                result = c.post("/messages/new", data={"text": "Hello"})
                self.assertEqual(result.status_code, 302)
                
                sess[CURR_USER_KEY] = not self.testuser.id
                
                result2 = c.post(f"/messages/{self.testuser.id}/delete", data=msg)
                self.assertEqual(result2.status_code, 404)
