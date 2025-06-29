import unittest
from eachare_app.connection import Connection

class TestAbbreviateMessage(unittest.TestCase):

    def setUp(self):
        self.connection = Connection("127.0.0.1", 8080, None)

    def test_abbreviate_message(self):
        # Test case: Normal message with short base64 content
        message = "127.0.0.1:8080 5 FILE arquivo.txt 0 0 base64content"
        expected = "127.0.0.1:8080 5 FILE arquivo.txt 0 0 base64content"  # No shortening needed
        result = self.connection.abbreviate_message(message)
        self.assertEqual(result, expected)

        # Test case: Normal message with long base64 content
        long_content = "a" * 50
        message = f"127.0.0.1:8080 5 FILE arquivo.txt 0 0 {long_content}"
        expected = f"127.0.0.1:8080 5 FILE arquivo.txt 0 0 {long_content[:30]}..."
        result = self.connection.abbreviate_message(message)
        self.assertEqual(result, expected)

        # Test case: Message with fewer fields
        message = "127.0.0.1:8080 5 HELLO"
        expected = "127.0.0.1:8080 5 HELLO"
        result = self.connection.abbreviate_message(message)
        self.assertEqual(result, expected)

        # Test case: Empty message
        message = ""
        expected = ""
        result = self.connection.abbreviate_message(message)
        self.assertEqual(result, expected)

if __name__ == "__main__":
    unittest.main()
