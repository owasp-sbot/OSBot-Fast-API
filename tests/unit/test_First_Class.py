from unittest import TestCase

from osbot_fast_api.First_Class import First_Class


class test_First_Class(TestCase):

    def setUp(self):
        self.first_class = First_Class()

    def test_name(self):
        assert self.first_class.name == 'First Class'

