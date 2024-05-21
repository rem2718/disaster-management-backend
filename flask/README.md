# UGV-Based Disaster Management Backend

## How to Run It:

- Create a virtual environment and activate it:
    ```
        python -m venv .venv
    ```
    ``` 
        source .venv/bin/activate # for linux
        # OR
        .venv/Scripts/Activate # for windows
    ```

- Run this code to install all required packages:
    ```
        pip install -r requirements.txt
    ```

- Place .env file inside _app_ folder

- Finally run this command to start the server:

    ```
        flask run
    ```

## Note:
Each time you want to run the server, make sure to refresh the project folder (if your folder is already cloned) + Don't forget to install the requirements. 

## Swagger:
To access the Swagger documentation for this server, simply visit the "/swagger" endpoint (127.0.0.1:5000/swagger) in your browser. Here, you'll find all the information about the APIs, and you can even test them directly within the Swagger interface.