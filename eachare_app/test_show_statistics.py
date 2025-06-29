import unittest
from eachare_app.main import add_download_statistics, show_statistics
from io import StringIO
import sys
from eachare_app.utils import print_with_lock

class TestShowStatistics(unittest.TestCase):

    def setUp(self):
        # Redirect stdout to capture print output
        self.held_output = StringIO()
        sys.stdout = self.held_output

    def tearDown(self):
        # Reset stdout
        sys.stdout = sys.__stdout__
        # Print the captured output for visibility
        print_with_lock("Captured Output:")
        print_with_lock(self.held_output.getvalue())

    def test_show_statistics(self):
        # Add sample statistics
        add_download_statistics(5.0, 1000, 256, 3)
        add_download_statistics(6.0, 1000, 256, 3)
        add_download_statistics(7.0, 1000, 256, 3)

        # Call show_statistics
        show_statistics()

        # Capture output
        output = self.held_output.getvalue()


        # Check if statistics are displayed correctly
        self.assertIn("256", output)  # Chunk size
        self.assertIn("3", output)    # Number of peers
        self.assertIn("1000", output) # File size
        self.assertIn("3", output)    # Count
        self.assertIn("6.00000", output)  # Mean
        self.assertIn("1.00000", output)  # Standard deviation

if __name__ == "__main__":
    unittest.main()
