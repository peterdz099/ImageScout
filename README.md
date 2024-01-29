# ImageScout

Image scout is a software for searching most similar figures in the large datatabase of images comming from scientific publications. 

## Running on Linux operation system

Clone git repository
  ```sh
    git clone https://github.com/peterdz099/ImageScout.git
  ```

Change the current working directory
  ```sh
    cd ImageScout
  ```

Add execute permission to ```setup.sh``` file.
  ```sh
    chmod +x setup.sh
  ```

Run the bash script that creates empty database and sets up the project
  ```sh
    ./setup.sh
  ```

Run virual environment
  ```sh
    source venv/bin/activate
  ```

Run the project on localhost
  ```sh
    python manage.py runserver
  ```

## Usage

To play around with the software you can login using ```admin``` login and ```ImageScout01``` password and simply add the **animals.pdf** to the database using GUI. After that you can test other features using images and PDF file from ```/testing``` directory. To manage the database as an admin user just go to ```http://127.0.0.1:8000/admin``` page and login as before. 
