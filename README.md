## Prerequisites
- Python 3
- MySQL Database

Setup a MySQL database, if you have Docker, run the following command to create the database container
```shell
docker run --name mysql -e MYSQL_ROOT_PASSWORD=password -e MYSQL_DATABASE=cms -p 3306:3306 -d mysql:5
```

Then in your configuration, update the `DATABASE_URI` value to
```..env
DATABASE_URI=mysql+pymysql://root:password@localhost:3306/cms
```

## Getting started
To get started, duplicate the `example.env` and rename the duplicated file to `.env`. Update the configuration
in the new `.env` file accordingly.

Run this command to create the virtual env folder
```shell
python3 -3 -m venv venv
```

Then activate the environment
```shell
. venv/bin/activate
```

Install the required packages
```shell
pip install -r requirements.txt
```

Then run the migration process to create the database structure needed by the application
```shell
flask db upgrade
```

Run the application when the migration completed.
```shell
flask run
```

## Package management
If we are adding new package to the project, after run `pip install` command,
run `pip freeze > requirements.txt` to update the `requirements.txt` file.
It is advisable to run 
```
pip install -r requirements.txt
``` 
after pulling latest code from repository.

## Database migration
1. Create a model.
2. Import it in `webapp/__init__.py`, after the line `db.init_app(app)`.
3. Generate new migration file using the following command
    ```shell
    flask db migrate -m "migration message"
    ```
4. Run `flask db upgrade` to apply the migration.
5. Run `flask db downgrade` to revert the migration.

> Note
1. Migration file will be generated in `migrations/versions` folder.
2. Do a migration everytime you pull latest changes from repository.
3. At any given time, only one migration (pending for upgrade) is allowed.
4. If you have a migration file that hasn't been upgraded yet and trying to
generate new migration file, you will get and error.
5. You can either run the upgrade command to apply the migration file first, or 
delete the migration file and regenerate a new migration file again.
6. Refer to [flask-migrate document](https://flask-migrate.readthedocs.io/en/latest/) for 
more information.

## Logging
When the system started a custom logger will be created and to be passed to subsequent 
modules. To use the logger, for example, refer to `webapp/user/controllers.py` on how to
get the logger from arguments and use it in the code. The configuration file consists 2 logging configurations. 
> Note this logger is not the same as the Flask built-in logger, the configurations will have no effect.
1. LOG_LEVEL - this is the log level to be used for the code
2. LOG_FORMAT - this is the format of the logged message


Currently logging will stream to console output instead of file.


## API Documentation
We are using Swagger UI to document the API, refer to `webapp/user/controllers.py` on how we can 
document our API. To access the Swagger UI, go to http://localhost:5000/apidocs/ after you started the
application. The path can be configured in the `SWAGGER` dictionary in `config.py` file. 
For more information, refer to [Flasgger official documentation](https://github.com/flasgger/flasgger).


## Request Parsing
In the official Flask documentation, it advises not to use the built in request parsing library, 
and instead to use something like [Marshmallow](https://marshmallow.readthedocs.io/en/stable/). 
Marshmallow can be used to wrap request parameter into an object, and validate it, it also can 
be used as a serialize/deserialize library as well. Refer to `webapp/user/controllers.py`,
we have 3 schemas, one is used for API response, while the other two are used for validating
input data. 

When this seems like duplicate work, where we also using 
[Schematics](https://schematics.readthedocs.io/en/latest/). The idea behind this setup is,
Marshmallow is used to validate request parameters at the *controller* layer, for example, 
to check if the parameter exist, or conform to certain format, where Schematics is meant to validate the 
command object passed into the *service* layer instead.

## Monitoring
In this setup, we will be using [Amazon X-ray](https://aws.amazon.com/xray/) to monitor
API. It will by default log the API latency, and log the error if there is any.
Here are some screenshot of X-Ray

### Trace List
![Trace list](docs/images/trace-list.png?raw=true "Trace List")

### Call Stack
![Call Stack](docs/images/call-stack.png?raw=true "Call Stack")

### Call Stack with exceptions
![Call Stack](docs/images/call-stack-with-exception.png?raw=true "Call Stack")

### Exceptions
![Exceptions](docs/images/exceptions.png?raw=true "Exceptions")


### Custom sub-segment
By default the X-ray middleware will create one segment per API call. If we want to create a sub-segment in call stack,
we can add annotation to the function, for example. There are few more ways to add sub-segment, do refer to the 
[documentation](https://docs.aws.amazon.com/xray/latest/devguide/xray-sdk-python-subsegments.html) for more information.

Add the annotations like this
```python
@xray_recorder.capture('## find_by_id')
def find_by_id(self, request: GetUserRequest):
    ... the rest of the codes
```

And in the call stack we will see the sub-segment
![Sub segment](docs/images/sub-segment.png?raw=true "Sub Segment")

>Note
> - that the tracing might not work correctly when the `FLASK_DEBUG` flag is turned on, reason being the 
debugger will overwrite the custom error handling logic and errors will not be sent to AWS X-ray for recording.
> - set 'AWS_XRAY_SDK_ENABLED' to `False` in `.env.test` file to disable sending trace data to AWS X-ray.

### Run AWS X-ray locally
1. [Download AWS X-ray daemon](https://docs.aws.amazon.com/xray/latest/devguide/xray-daemon.html)
2. Run the daemon 
    ```bash
    ./xray_mac -o -n ap-southeast-1
    ```
3. X-ray Daemon will run at `127.0.0.1:2000`
4. Change the value of `XRAY_DAEMON_URL` in `.env` file to update the daemon url accordingly.


## Pre commit hook
To make the code more standardized, we have setup a pre commit hook in the project, where when a developer 
is committing codes using Git commit, it will trigger the commit hook and format the code accordingly. 
At the moment we are using [Black](https://github.com/psf/black) and
[Flake8](http://flake8.pycqa.org/en/latest/) to format the code and check the style.


## Testing
### Pre-requisites
Duplicate `example.env` to `.env.test`, the test runner will load the environment variable from this file.

### How to create and run test cases
Create test cases and put in the `tests` folder, file name must in begin with `test_`.

Type `pytest` to run the all test cases.

Type `coverage report --include=webapp/**/*` to generate coverage report.

Each test file will have a `setup` and `teardown` function, `setup` will be triggered before running any test and 
`teardown` will be triggered when all test cases in the file finished running. 

During `setup`, we will create a test environment by loading the test config, and create an empty database. We will
run the migration script and create the necessary tables. We can also populate some test data for testing purpose.



### TODO
