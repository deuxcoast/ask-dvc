# ask-dvc

### commands for setting up the project

**All of these commands should be run from the base directory of the
project**. So after cloning the project, we should `cd` into the repository.

1. Clone the project. `cd` into the directory you want the project to be
   stored in, then run the following command:

   `git clone https://github.com/deuxcoast/ask-dvc.git`

2. `cd` into the directory we just downloaded, this is where all of the
   project files are.

   `cd ask-dvc`

3. Create a virtual environment.

   `python3 -m venv .venv`

4. Activate the virtual environment

   `source .venv/bin/activate`

5. Download the dependencies required to run the project, as listed in the
   `requirements.txt` file.

   `pip install -r requirements.txt`

6. Run the migrations necessary to bring the database up to the correct
   state.

   `python manage.py migrate`

7. Spin up the development server and get going!

   `python manage.py runserver`
