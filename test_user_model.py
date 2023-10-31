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

    def test_user_model(self):
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
        self.assertEqual(u.bio, None)
        self.assertIn(f"<User #{u.id}: {u.username}, {u.email}", repr(u))
    
    def test_is_followed_by(self):
        """Do the following/followed methods work?"""
        u1 = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )
        u2 = User(email = 'hjkl@asdf.com',
                  username = "testuser2",
                  password = "secretkey")
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        u1followu2 = Follows(user_being_followed_id = u2.id, user_following_id = u1.id)
        db.session.add(u1followu2)
        db.session.commit()

        self.assertFalse(u1.is_followed_by(u2))
        self.assertTrue(u2.is_followed_by(u1))
        self.assertFalse(u2.is_following(u1))
        self.assertTrue(u1.is_following(u2))

    def test_signup_good_info(self):
        u = User.signup('bob','asdf@asdf.com','secretkey', '')
        db.session.commit()

        self.assertTrue(u.id)

    def test_signup_bad_info(self):
        u = User.signup('','','secretkey','')
        try:
            db.session.commit()
        except ValueError:
            self.assertFalse(u.id)
    
    def test_authenticate(self):
        u1 = User.signup(email = 'hjkl@asdf.com',
                  username = "testuserlogin",
                  password = "secretkey",
                  image_url = '')        
        db.session.add(u1)
        db.session.commit()

        self.assertTrue(User.authenticate('testuserlogin','secretkey'))
        self.assertFalse(User.authenticate('testuserlogin','wrongpassword'))
        self.assertFalse(User.authenticate('WrongUsername','secretkey'))
