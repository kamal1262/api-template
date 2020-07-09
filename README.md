# API Template [![Build status](https://badge.buildkite.com/fcf0099ac96f18da2729ebcafe9ec525c471b84ce7ac969873.svg)](https://buildkite.com/rea/api-template)

## To use this project
Click on the `Use this template` button, follow the instruction to create a new project.
![Use this template button](docs/images/use-this-template.png?raw=true "Use this template")

>Note: Please update the README file accordingly after creating your own project.

## Prerequisites
- Python 3
- MySQL Database


## Getting started
To get started, duplicate the `example.env` and rename the duplicated file to `.env`. Update the configuration
in the new `.env` file accordingly.

Run this command to create the virtual env folder
```shell
python3 -m venv venv
```

Then activate the environment
```bash
. venv/bin/activate
```

Install the required packages
```bash
pip install -r requirements.txt
```

Install pre-commit hook
```bash
pre-commit install
```

Create `.env` file from `example.env`
```bash
cp example.env .env
```

### Local database setup
Setup a MySQL database, if you have Docker, run the following command to create the database container
```shell
docker run --name mysql -e MYSQL_ROOT_PASSWORD=password -e MYSQL_DATABASE=commonsDB -p 3306:3306 -d mysql:5
```

Then in `.env`, update the `DATABASE_URI` value to
```..env
DATABASE_URI=mysql+pymysql://root:password@localhost:3306/commonsDB
```

### Using AWS dev database
Add to your `~/.ssh/config` file with below script. If you don't have private key `aws-account-bastioninstance.pem` file, please request from ops channel.
```
Host engineering.dev
    HostName 52.77.243.251
    IdentityFile <Path to .pem file>
    LocalForward 3306 commons-db-dev-auroracluster-1om7npo4s577o.cluster-ro-csypt18aokzy.ap-southeast-1.rds.amazonaws.com:3306
    RequestTTY no
    User ec2-user
```

Then in `terminal`, run `ssh engineering.dev` to connect to the instance through ssh.
Now you can connect to the database through `127.0.0.1` and inside `.env`, update the `DATABASE_URI` value to
```..env
DATABASE_URI=mysql+pymysql://dbuser:password@127.0.0.1:3306/commonsDB
```

### Loading data into database
Run the migration process to create the database structure needed by the application
```bash
flask db upgrade
```

Run the application when the migration completed.
```bash
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

> Tips: you can run the pre-commit manually with the following command 
  ```
  pre-commit run  --all-files
  ```

## Queue and asynchronous processing
Asynchronous processing is useful when we have tasks that we want to process on a different thread, a very common use case is 
sending emails, in most cases, we won't have to wait for the whole email sending process to complete before we continue to 
another process.

To use queue, we need to have a publisher and consumer. Every publisher and consumer will be using one topic.
- Producer will be the code that create and send the payload to a queue.
- Consumer will take payload from queue and process it.

There will be 3 different scenarios
- The code will consist the publisher and consumer code.
- The code only consist the publisher code, with the assumption that some other services outside of this application context.
- The code only consist the consumer code, with the assumption that this application is processing payload published by others.

### Configuration
You can configure the queue behavior in `.env` file.
`MESSAGE_TOPICS=topic,topic2`
- define how many topics you will be using in the system

`TOPIC_CONSUMERS=topic:InMemoryConsumer,topic2:InMemoryConsumer`
- define the consumers and types of each consumer

`PUBLISHER_TYPE=InMemoryPublisher`
- define the publisher type

At the moment the code supports `InMemory` and `SQS` for both publisher and consumer. Do refer to these codes when you
want to create new publisher or consumer. `InMemory` should only be used in development or testing environment.

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
- Found some issues with AWS-Xray SDK library, trace data will not be streamed back to X-ray when SQL inspection is turned
on and exception happened during the API call, need some time to look into it.