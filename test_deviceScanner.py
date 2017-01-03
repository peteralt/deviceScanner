import unittest
from deviceScanner import *

class DevicesTestCase(unittest.TestCase):
    """Tests for `deviceScanner.py`."""

    def test_can_run_nmap_and_return_mac_addresses(self):
        """Can we run nmap as sudo and get mac addresses back?"""
        scanner = deviceScanner()
        results = scanner.scan()
        self.assertIsNotNone(results)
        self.assertTrue(len(results) > 0)
        self.assertIn('mac', results[0])
        self.assertIn('ip', results[0])
        self.assertIn('vendor', results[0])

    def test_can_save_results_in_database(self):
        scanner = deviceScanner()
        results = scanner.scan()
        for device in results:
            result = scanner.saveDevice(device)
            self.assertIsNotNone(result)

    # def test_can_post_device_to_backend(self):
    #     """Can we post a device to the backend service and get a 200 response back?"""
    #     scanner = deviceScanner()
    #     results = scanner.scan()
    #     for device in results:
    #         response = scanner.postDevice(device)
    #         self.assertEqual(200, response)

if __name__ == '__main__':
    unittest.main()
