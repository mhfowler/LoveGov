
celery
pip install -U Celery
pip install django-celery
python manage.py migrate djcelery
brew install rabbitmq
OR sudo apt-get install rabbitmq-server
pip install librabbitmq
pip install pika==0.9.5
pip install supervisor

********** GETTING STARTED ************

Now that you have checked out a version of the project and installed all the dependencies you should be pretty much ready to go. 

FRIENDLY SCRIPTS FOR NON-CODERS:
Open up terminal and navigate to your checked out version of the project and run:
'./local_setup.sh' 
'./local_server.sh'

and if everything has gone to plan, you should now have your own local lovegov running at http://127.0.0.1:8000/. Whenever you want to restart the local server, run './local_server.sh'.

FOR CODERS AND THE INCLINED:
Those scripts barely do anything, the first one syncs the local database and initializes it with some testdata. The second is a paper-thin wrapper for django's built in development server. You should be able to make changes to the project now and see what happens by running the local server. This is step 1 of our workflow, the rest of which will be elucidated below.


********** THE WORKFLOW ************

You'll probably want to download PyCharm, an IDE for python+django. We like it, but if you have another IDE you would like to use go for it! 
http://www.jetbrains.com/pycharm/

On to some real stuff,
'/lovegov' is the django project we work with.

There are three different settings files at the root of the project, reflecting the three different phases of our workflow.

'/lovegov/local_settings' 	your local server
'/lovegov/dev_settings' 	served by dev.lovegov.com
'/lovegov/live_settings'	served by lovegov.com

All three phases of the workflow make use of the same code to avoid errors arising between the turnover from testing to live. This is to make sure that anything we are releasing to the public can be thoroughly tested. Throughout this document, and in our naming conventions, local/live/dev will refer to the three locations above.

1) Make changes locally.
2) Test on local server.
3) 'devupdate' on actual server.  
-- at this point your changes will be fully reflected on novavote.com but will not have any effect on lovegov.com
4) Test on dev.lovegov.com
5) 'liveupdate' on actual server.
-- after this lovegov.com should be in the exact same state as dev.lovegov.com as you were testing it.


********** AMAZON EC2 ************

ip + password: talk to me

I will refer to directories in this section relative to the server directory structure, not the repository relative paths.

'/srv/dev'	:	dev branch
'/srv/live'	:	live branch
'/srv/server': server config files (git branch)
'/static/dev'	:	static files served by url dev.lovegov.com/static
'/static/live'	:	static files served by url lovegov.com/static
'/media/dev'  :	user uploaded files served by url dev.lovegov.com/media
'/media/live'	: user uploaded files served by url lovegov.com/media
'/log/dev'	:	text logs for the dev project
'/log/live'	:	text logs for the live project


********** ALIASES ************

We have created a number of useful command aliases to improve efficiency, but mostly to simplify our workflow and reduce errors.

Locally add this line to your ~/.bash_profile (or <operating system> equivalent)
source /local_aliases.sh

Now when you open a new terminal shell, you will have access to a number of aliases having to do with our project and workflow. We also have a similar set of aliases available when you ssh into the server.


********** THE PROJECT ************

~ 

********** SASS SETUP *************

We are using Sassy CSS (SCSS) which is compiled to CSS. See http://sass-lang.com/ for more information. 


