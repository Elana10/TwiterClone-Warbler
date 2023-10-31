"""Message Model tests."""
import os
from unittest import TestCase

from models import db, User, Message, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app

db.create_all()

class MessageModelTestCase(TestCase):
    """ Tests  Message Model """

    def setUp(self):
        """Create test """
        self.client = app.test_client()
        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        user = User(
            email = "test@test.com",
            username= 'testuser',
            password = "HASHED_PASSWORD")
        
        db.session.add(user)
        db.session.commit()

        self.user = user

        message = Message(
            text = 'Test Message',
            user_id = user.id
        )

        db.session.add(message)
        db.session.commit()

        self.message = message
    
    def tearDown(self):
        """Clean up fouled transactions."""
        db.session.rollback()
    
    def test_message_model(self):
        """Calls the one message from setup and tests its properties."""
        m = Message.query.get(self.message.id)

        self.assertTrue(m)
        self.assertEqual(m.id, self.message.id)
        self.assertEqual(m.text, "Test Message")
        self.assertEqual(m.user_id, self.user.id)
    
    def test_calling_message_through_user(self):
        """Calls the message through the User relationship."""
        m = Message.query.filter_by(user_id = self.user.id)

        self.assertTrue(m)
    
    def test_add_more_messages(self):
        """Add more messages to user."""

        message2 = Message(
            text = 'This is message 2.',
            user_id = self.user.id
        )

        db.session.add(message2)
        db.session.commit()

        self.assertTrue(message2.id)
        self.assertTrue(message2.timestamp)

