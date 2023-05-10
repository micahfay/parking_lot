To run this project you will need to have docker installed on your machine.

Once you've cloned the repository cd into the directory,

Then run `docker compose up`.

You may have to `ctrl+c`, `docker compose down`, and `docker compose up` to get it running initially. the db seems to lag on initial boot.

Once it's running you can access the api docs at localhost:8000/api/docs/ on your machine.

There are a limited number of tests in the repo only for the most essential functions. you can run them with the command:
`docker compose run --rm web python manage.py test`
