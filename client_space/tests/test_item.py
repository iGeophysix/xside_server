"""
Test 1:
SetUp:
- Create 2 clients
- Create user and link user to one client
- Create one item and link it to client
test:
- request all items - get one created
- request created item - get 200 and item info
- request non-existing item - get 404 Not found
- request without authorization - get 401 Not authorized
- request creation of a new item with correct parameters - get 200, check images are uploaded, check polygons are created
- request creation of a new item with wrong parameters - get 400 for each wrong parameter
- request POST a new Item, PUT with updates, DELETE the Item
- request POST a new Item, POST the same message - get 401 about duplicated name
- write tests for each validation in item.save_item
"""