from django.test import TestCase

# Create your tests here.

"""
Test 1:
SetUp:
- Create 2 clients
- Create user and link user to one client
test:
- request all clients - get one linked
- request linked client - get 200 and info about the linked client
- request non-linked client - get 404 Not found 
- request without authorization - get 401 Not authorized
"""

"""
"""