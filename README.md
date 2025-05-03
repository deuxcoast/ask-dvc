# askDVC

askDVC is a place for students to ask questions, provide answers and make life a
little easier for each other. The idea is to have a central place where students
can come to ask questions about their classes,teachers, and life as a student at
large.

![askDVC Homepage](./resources/homepage.png)

Whether it's questions about which professor to take, how manageable 20
credits in a semester is, where the best place on campus to study is, or
advice on making friends - askDVC aims to create a place where knowledge is
pooled, and student's can share their experiences.

![askDVC post example](./resources/post.png)

---

askDVC was built over 4 weeks as part of Project Bracket at Diablo Valley
College.

![Project Bracket logo](./resources/project-bracket-logo.png | width=150)

## Team Members

#### Aanya

Github: (@FlyHighStem)[https://github.com/FlyHighStem]

#### Conor

Github: (@deuxcoast)[https://github.com/deuxcoast]

#### Jordan

Github: (@jayracher)[https://github.com/jayracher]

#### Karen

Github: (@karen2zhao)[https://github.com/karen2zhao]

#### Matthew

Github: (@mattag1234)[https://github.com/mattag1234]

---

### Instructions for setting up the project

**All of these commands should be run from a terminal in the base directory of
the project**. After cloning the project, we should `cd` into the repository.

> [!NOTE]
> These commands are for zsh/bsh shells, which should work for most Mac OS and
> Linux users. For Windows users the commands below may be different.

1. Clone the project. To do this, `cd` into the directory you want the project
   to be stored in, then run the following command:

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
