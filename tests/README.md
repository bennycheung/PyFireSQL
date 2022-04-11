# Flask Unit and Integration Tests using `pytest`
Allow PyFireSQL to use unit and integration testing.

## Technical Details
We prefer `pytest` since it:

* Requires less boilerplate code so your test suites will be more readable.
* Supports the plain assert statement, which is far more readable and easier to remember compared to the assertSomething methods -- like assertEquals, assertTrue, and assertContains -- in unittest.
* Is updated more frequently since it's not part of the Python standard library.
* Simplifies setting up and tearing down test state.
* Uses a functional approach.
* Supports fixtures.

```python
def test_get_custom_token(test_client):
	"""
	GIVEN a user email
	WHEN get the user custom token
	THEN check custom token is not None
	"""
	email = 'captain.america@avengers.com'
	custom_token = test_client.get_user_custom_token(email)
	assert custom_token != None
```

After the import, we start with a description of what the test does:

```
	"""
	GIVEN a user email
	WHEN get the user custom token
	THEN check custom token is not None
	"""
```

Tests are one of the most difficult aspects of a project to maintain. Often, the code (including the level of comments) for test suites is nowhere near the level of quality as the code being tested.

A common structure used to describe what each test function does helps with maintainability by making it easier for a someone (another developer, your future self) to quickly understand the purpose of each test.

A common practice is to use the GIVEN-WHEN-THEN structure:

* GIVEN - what are the initial conditions for the test?
* WHEN - what is occurring that needs to be tested?
* THEN - what is the expected response?

For more, review the [GivenWhenThen](https://martinfowler.com/bliki/GivenWhenThen.html) article by Martin Fowler and the [Python Testing with pytest](https://pragprog.com/titles/bopytest/python-testing-with-pytest/) book by Brian Okken.

### Fixtures
Fixtures initialize tests to a known state in order to run tests in a predictable and repeatable manner.

The test fixture approach provides much greater flexibility than the classic Setup/Teadown approach.

pytest-flask facilitates testing Flask apps by providing a set of common fixtures used for testing Flask apps. This library is not used in this tutorial, as I want to show how to create the fixtures that help support testing Flask apps.

First, fixtures are defined as functions (that should have a descriptive names for their purpose).

Second, multiple fixtures can be run to set the initial state for a test function. In fact, fixtures can even call other fixtures! So, you can compose them together to create the required state.

Finally, fixtures can be run with different scopes:

* function - run once per test function (default scope)
* class - run once per test class
* module - run once per module (e.g., a test file)
* session - run once per session

For example, if you have a fixture with module scope, that fixture will run once (and only once) before the test functions in the module run.

Fixtures should be created in `tests/conftest.py`.

### Unit Test Example
To help facilitate testing, we can add a fixture to `tests/conftest.py` that is used to create a HIVE client to test:

```python
# return a test client using emulators
@pytest.fixture(scope='session')
def test_client():
	hiveClient = HiveClient()
	hiveClient.use_emulator()
	hiveClient.setup(env_mode="dev", credentials_path="credentials")
	yield hiveClient
```

The `@pytest.fixture` decorator specifies that this function is a fixture with module-level scope. In other words, this fixture will be called one per test module.

This fixture, new_user, creates an instance of User using valid arguments to the constructor. user is then passed to the test function (return user).

We can simplify the `test_sign_in_with_email_password()` test function from earlier by using the `test_client` fixture:

```python
def test_sign_in_with_email_password(test_client):
	"""
	GIVEN a user email/password
	WHEN sign-in with email and password
	THEN success to sign-in with the user access token
	"""
	email = 'captain.america@avengers.com'
	response = test_client.sign_in_with_email_and_password(email, 'password')
	assert response['idToken'] != None'
```

By using a fixture, the test function is reduced to the assert statements that perform the checks against the User object.

## Integration Test 
The second class of tests that we're going to write is an integration test for `<some_modules>/routes.py`,
which contains the view functions for the module blueprint.

Since this test is an integration test, it should be implemented in `tests/integration/test_<something>.py`, for example:

```python
def test_routes_gate_url(test_app_client):
	"""
	GIVEN company avengers and device alpha
	WHEN get the '/gate/url' page is requested
	THEN check that the response is valid
	"""
	companyId = 'avengers'
	deviceId = 'alpha'
	apiKey = 'token'
	request_url = '/gate/url?company={}&device={}&apiKey={}'.format(companyId, deviceId, apiKey)
	response = test_app_client.get(request_url)
	data = json.loads(response.data)

	assert response.status_code == 200
	assert data['company'] == 'avengers'
	assert data['displayName'] == 'Front Profile'
	assert data['visitorUrl'] != None
	assert data['userUrl'] != Non
```

### Using Fixture
To help facilitate testing all the view functions in the Flask project, a fixture can be created in `tests/conftest.py`.
This project created the Flask application in module. Therefore, the `app` has been precreated. We shall construct a Flask client `test_app_client` and Hive client fixtures for tests to use.

```python
from app import app, hiveclient

# return a Flask test client using emulators
@pytest.fixture(scope='session')
def test_app_client():
	with app.test_client() as testing_client:
		# established an applicaiton context
		with app.app_context():
			yield testing_client

# return a test client using emulators
@pytest.fixture(scope='session')
def test_client():
	with app.app_context():
		yield hiveclient
```

In order to create the proper environment for testing, Flask provides a `test_client` helper. This creates a test version of our Flask application,
which we used to make a GET call to the '/...' URL. We then check that the status code returned is OK (200) and that the response contained the expected result.

The test function, starts with the GIVEN-WHEN-THEN description of what the test does. Next, a Flask application client `test_app_client` is injected:

> We are using BeautifulSoup4 to parse and process the HTML page

```python
from bs4 import BeautifulSoup

def test_routes_gate_admit_visitor(test_app_client):
	"""
	GIVEN company avengers and hive gate profile
	WHEN get the '/gate/admit' with visitor mode is requested
	THEN check that the response is visitor admit page
	"""
	companyId = 'avengers'
	profileId = 'pHhAU2YuWQ1ymIHBLwat' # Front Profile
	embed = 0
	mode = 'visitor'
	lang = 'en'
	apiKey = 'token'
	request_url = '/gate/admit?company={}&profile={}&embed={}&lang={}&apiKey={}'.format(companyId, profileId, embed, lang, apiKey)

	response = test_app_client.get(request_url)
	assert response.status_code == 200

	# parse response HTML to verify
	soup = BeautifulSoup(response.data, 'html.parser')
	title = soup(text="Front Profile")
	assert title == ["Front Profile"]

	# only 1 location will has a checked radio
	choice = soup.find('input', attrs={'name':'checkin'}).has_attr('checked')
	assert choice == True
```

These checks match with what we expect the page to see when we navigate to the `/gate/admit` URL.

Notice how much duplicate code is eliminated by using the `test_app_client` fixture? By utilizing the `test_app_client` fixture, each test function is simplified down the HTTP call (GET or POST) and the assert that checks the response.


### Notes
> To learn more about the Application context in Flask, refer to the following blog posts:
>
> Basics: [Understanding the Application and Request Contexts in Flask](https://testdriven.io/blog/flask-contexts/)
> Advanced: [Deep Dive into Flask's Application and Request Contexts](https://testdriven.io/blog/flask-contexts-advanced/)

The yield testing_client statement means that execution is being passed to the test functions.


## Running the Tests
To run the tests, run pytest in the top-level folder for the Flask project:

```
$ pytest

tests/unit/test_hive_client.py .....                                                                [ 71%]
tests/unit/test_hive_company.py ..                                                                  [100%]

========= 7 passed in 0.33s ============
```

To see more details on the tests that were run, use `-v` option:

```
$ pytest -v

tests/unit/test_hive_client.py::test_client_must_be_setup PASSED                                    [ 14%]
tests/unit/test_hive_client.py::test_get_custom_token PASSED                                        [ 28%]
tests/unit/test_hive_client.py::test_get_access_token PASSED                                        [ 42%]
tests/unit/test_hive_client.py::test_sign_in_with_email_password PASSED                             [ 57%]
tests/unit/test_hive_client.py::test_https_oncall_update_company PASSED                             [ 71%]
tests/unit/test_hive_company.py::test_company_doc PASSED                                            [ 85%]
tests/unit/test_hive_company.py::test_company_collections PASSED                                    [100%]

======== 7 passed in 0.29s =======
```

If you only want to run a specific type of test:

```
pytest tests/unit/
pytest tests/integration/
```

During development, we want to see the test `print` output, we can run with `pytest -s` to see the stdout and stderr output.

## Test Coverage
We are using `pytest-cov` to assist code coverage reports. Make sure that we have install,

```
pip install pytest-cov
```


Measure the amount of code coverages with the tests by,

```
pytest --cov-report html:coverage --cov=hiveoffice tests
```

The report is generated as HTML into `coverage` folder.
