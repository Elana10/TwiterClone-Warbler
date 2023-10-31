# ""User View tests."""

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
        
        self.messageWorld = Message(text = 'Hello World', user_id = self.testuser.id)
        db.session.add(self.messageWorld)
        db.session.commit()
    
    def test_home_view(self):
        """Checks the home page."""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            resp = c.get("/users")
            html = resp.get_data(as_text = True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('@testuser', html)
    
    def test_user_page(self):
        """Checks the user page loads correctly."""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id        
            resp = c.get(f'/users/{self.testuser.id}')
            html = resp.get_data(as_text = True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Edit Profile', html)
    
    def test_following_page(self):
        """Checks the user's following page for listed users."""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id     

            user2 = User(
                username = 'Bella',
                email = 'qwer@qwer.com',
                password = "HASHED_PW"
            )
            db.session.add(user2)
            db.session.commit()

            following = Follows(
                user_being_followed_id = user2.id,
                user_following_id = self.testuser.id
            )
            db.session.add(following)
            db.session.commit()

            resp = c.get(f'/users/{self.testuser.id}/following')
            html = resp.get_data(as_text = True)    

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Bella', html)    

    def test_followers_page(self):
        """Checks the user's following page for listed users."""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id     

            user2 = User(
                username = 'Sam',
                email = 'qwer@qwer.com',
                password = "HASHED_PW"
            )
            db.session.add(user2)
            db.session.commit()

            followers = Follows(
                user_being_followed_id = self.testuser.id,
                user_following_id = user2.id
            )
            db.session.add(followers)
            db.session.commit()

            resp = c.get(f'/users/{self.testuser.id}/followers')
            html = resp.get_data(as_text = True)    

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Sam', html)

    def test_stop_following(self):
        """Checks the user's following page for listed users."""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id     

            user2 = User(
                username = 'Sam',
                email = 'qwer@qwer.com',
                password = "HASHED_PW"
            )
            db.session.add(user2)
            db.session.commit()

            followers = Follows(
                user_being_followed_id = user2.id,
                user_following_id = self.testuser.id
            )
            db.session.add(followers)
            db.session.commit()

            resp = c.post(f'/users/stop-following/{user2.id}', follow_redirects = True)
            html = resp.get_data(as_text = True)    

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn('Sam', html)
    
    def test_profile_view_get(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get('/users/profile')
            html = resp.get_data(as_text = True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('testuser', html)

    def test_profile_view_get_post(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            data = {
                'username' : self.testuser.username,
                'password' : 'testuser',
                'email' : self.testuser.email,
                'bio' : 'This is a story about a cat named Bob.',
                'image_url' : 'image_url'
            }

            resp = c.get('/users/profile')
            resp2 = c.post('/users/profile')
            resp3 = c.post('/users/profile', data = data, follow_redirects = True)
            html = resp3.get_data(as_text = True)

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp2.status_code, 200)
            self.assertEqual(resp3.status_code, 200)
            self.assertIn('This is a story about a cat named Bob', html)


                    