import pytest
from firesql.firebase import Client

# fixtures can be run with different scopes:
# 
# * function - run once per test function (default scope)
# * class - run once per test class
# * module - run once per module (e.g., a test file)
# * session - run once per session

# return a test client using emulators
@pytest.fixture(scope='session')
def test_client():
	client = Client()
	client.use_emulator()
	client.connect(credentials_path="credentials")
	yield client
