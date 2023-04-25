import unittest
import os

import time_tracker


class TestYourModule(unittest.TestCase):
    def setUp(self):
        self.work_study_log_file = 'work_study_log.csv'
        self.work_task_tracker_file = 'work_task_tracker.csv'
        self.study_task_tracker_file = 'study_task_tracker.csv'
        self.work_time_log_file = 'work_time_log.csv'
        self.study_time_log_file = 'study_time_log.csv'

    def test_set_mode(self):
        # Test case where user is not clocked in
        your_module_name.set_mode()
        self.assertIsNone(your_module_name.mode)

        # Test case where user is clocked in
        with open(self.work_study_log_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Work'])
        file.close()
        your_module_name.set_mode()
        self.assertEqual(your_module_name.mode, 'Work')

    # Add more test cases for the other functions in your module

if __name__ == '__main__':
    unittest.main()
