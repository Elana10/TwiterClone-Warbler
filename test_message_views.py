"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User, Likes, Follows

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
        Likes.query.delete()

        db.create_all()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        db.session.commit()

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.order_by(Message.id.desc()).first()
            self.assertEqual(msg.text, "Hello")
    
    def test_add_message_view(self):
        """Will the form populate for users to add a message?"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get("/messages/new")
            html = resp.get_data(as_text = True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Add my message!", html)
    
    def test_view_message(self):
        """Will test the def messages_show feature."""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            msg = Message(
                text = 'Hello World',
                user_id = self.testuser.id
            )

            db.session.add(msg)
            db.session.commit()

            resp = c.get(f'/messages/{msg.id}')
            html = resp.get_data(as_text = True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Hello World', html)
    
    def test_delete_message(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            msg2 = Message(
                text = 'Bob is a builder.',
                user_id = self.testuser.id
            )        
            db.session.add(msg2)
            db.session.commit()      

            resp = c.post(f'/messages/{msg2.id}/delete')
            html = resp.get_data(as_text = True)

            self.assertEqual(resp.status_code, 302)
            self.assertNotIn('Bob is a builder', html)
            self.assertEqual(len(Message.query.all()), 0)
    
    def test_like_message_view(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            user2 = User(
                email='email@email.com',
                username='SecondUser',
                password='secretkey'
            )

            db.session.add(user2)
            db.session.commit()

            msg3 = Message(
                text='No School for Summer',
                user_id=user2.id
            )
            db.session.add(msg3)
            db.session.commit()

            testuser_follows = Follows(
                user_being_followed_id=user2.id,
                user_following_id=self.testuser.id
            )
            testuser_likes = Likes(
                user_id=self.testuser.id,
                message_id=msg3.id
            )
            db.session.add(testuser_likes)
            db.session.add(testuser_follows)
            db.session.commit()  # Commit changes before the first request

            resp = c.post(f"/users/add_like/{msg3.id}")
            db.session.commit()  # Commit changes after the first request

            resp2 = c.post(f"/users/add_like/{msg3.id}", follow_redirects=True)
            html = resp2.get_data(as_text=True)

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp2.status_code, 200)
            self.assertIn('primary', html)

