# E-LIB

Electronic book library created with Django Web Framework.

## Description


Users can authorize and authenticate. There are two roles with their own set of accesses: readers and librarians. To register, you need to provide a login and an email address.

In the user profile you can change login and e-mail.

The app also includes books, authors, and genres. Users can search for their favorite books or explore new genres and authors. 

Comments allow you to share your thoughts about the books with other users.

Ticket system allows users with only reader access to create tickets for books or authors modification. Librarians can accept or reject them.


## Tech stack

- Python 3.10
- Django 4.2
- PostgreSQL
- pip
- bootstrap-py
- django-crispy-forms
- Pillow


## Run

Start web application and database in Docker

### Clone project from git via ssh

```commandline
git clone git@github.com:kolaxy/library.git
```

### Cd into project folder 

```commandline
cd library
```

### Build application Docker image 

```commandline
docker build -t kolaxy/elib:1.0 .
```

### Run application and database containers

```commandline
docker compose --profile backend up -d
```