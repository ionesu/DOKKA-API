# DOKKA
Simple Rest API with Python Flask framework.

## Installation
Creat Virtual Environment
```bash
python3 -m venv venv
```
Run Virtual Environment
```bash
source venv/bin/activate
```
Install all the necessary packages
```bash
(venv) $ pip install -r requirements.txt
```
## Running

Running Flask application on [http://127.0.0.1:5000/](http://127.0.0.1:5000/) 
```bash
(venv) $ FLASK_APP=app.py flask run
```
Example of using API with cURL command line tools.
/api/getResult/ - It is an API to retrieve results of “/getAddresses” API
identified by “result_id” = UUID.
```bash
curl http://127.0.0.1:5000/api/getResult/<uuid_code>
```
## License
[Ivan Sushkov](https://github.com/ionesu)