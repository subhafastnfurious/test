### Screening task.

Hi there, this is part one of the recruitment process, we want to make
sure that you have reasonable grasp of some of the technologies we use
in the company: python, git, django, docker, django-rest-framework. There
is no correct way to solve this task, but don't get stressed, this is just
screening, not a complete display of your many skills, the solution does not
need to be perfect or complete. If you solved most of the explicit TODOs in
the repository, we want to talk to you.

The screening task takes form of a git repository that you should fork
(we don't give GitLab accounts, clone it via https)
on a non-public git host (bitbucket comes to mind, use any other, just not public
github). There are TODOs in the code and in the commit messages that you should
focus on. Don't stress over fixing all of them, don't make it perfect unless
you have too much free time, we expect you to spend about 4-6 hours on the task,
feel free to share how much time it took you so we can adjust for the future.

    git clone http://gitlab.softheart.io/open/screening_task.git

*There is no need to have an account on our Gitlab to clone this repository. No credentials required.*

The end goal is to have a working API, without frontend that can be started
using provided docker-compose.yml that we can query and get some data from.

When we receive your code, we will run this:

    docker-compose up -d
    docker-compose exec backend ./manage.py populate
    curl http://localhost:8000/office-spaces/ | grep -o zip_code | wc -l
    apt install jq
    curl http://localhost:8000/office-spaces/ | jq 0s
    and expect to get a number


Hints. The project:
- is not runnable due to broken config.
- does not follow best code formatting style in few places
- has broken DRF elements like views and serializers
- is missing some very common django parts like urls
- the Docker part is mainly complete but we have broken it in few places.
- there is User class provided but the API should return at least
  OfficeSpace.public "for free"

We use Ubuntu and test on Ubuntu. We expect you to use Linux (any) or MacOs and
be reasonably skilled in running Linux. The role requires managing Linux
servers.

### what's next

If we are happy with your solution and your resume, we will invite you
to a 30-45 hangout call with our technical people where you will be asked
two kinds of questions:

1) technical:

- some trivial (for example, what does python's super() do or what is
  Dockerfile's CMD ),

- some non-trivial to find out where you are at in terms of various
  technologies (how's Django's prefetch_related useful in practice?)

- and some that we expect you not to be able to answer that are specific
  problems that we encountered in our projects that should spur interesting
  conversations;

2) general interpersonal questions:

- we want to find out whether you fit in our company's culture well, there isn't
  a specific list of personal qualities that we are looking for and we are
  humans too ;) but at minimum we want to make sure that you are friendly and
  responsible. Let's have a nice chat about you, anything and everything.

Try not to ask us questions clarifying the task, the code or the repository,
you will sometimes get unclear requirements about the project and will have to
make do.

Best of luck!

