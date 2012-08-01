********** LOVEGOV README **********

Welcome to LoveGov, this readme is meant to get you up to speed with all aspects of our development process and able to contribute as soon as possible.


********** QUICK INTRO ************

The idea of LoveGov was born in the summer of 2011 and has been evolving ever since. We first started writing code in December. Our server was first put online in the beginning of February 2012. While we have maintained an abstract vision for LoveGov which has stayed fairly constant throughout this time, part of the joy and the beauty of working on this project is that it is all still brand new. LoveGov is a new medium for an old problem, which means the solutions are not yet all decided! 

I bring this up here at the beginning, because while this readme is trying to get you up to speed with what we have done, and while Yoshi, Catherine and I have probably talked to you about where we want to go.. how we get there is a morphous question that will be decided on the way. On a day to day basis, what features we offer, and how we implement them, are likely to change. If something has been implemented one way, and you think it can be done better a different way, tell us your idea and there will be no delay in replacing it if it is better. Similarly if you have questions about anything, do not hesitate to ask someone. We want to deliver a superior product and make LoveGov successful, if this is your goal then you are on my team--and as cliche as it may sound--if we are achieving this goal, then whose implementation we are using, or what feature we are discarding, is of no importance to me. 

Along these lines, also remember that this is a company formed and run by undergraduates. As LoveGov itself evolves over time, so do we, and a big part of working on this project is learning on the fly. Google has been our best friend in the development process, and as we grow and change, an end to the new problems which require new skills and more to learn, is nowhere in sight. But as self-reliance is valuable, being aware of your own limits and knowing when to look for help is just as important. Given our relative inexperience, our success will very much depend on our willingness and ability to seek out expert help and advice. If you can contribute to the project by finding good consult and sharing it with the team, this will be lauded just as if you had come up with the ideas yourself.

Lastly, even though it would be near impossible for us to take our vision for LoveGov and its mission any more seriously, let's not forget that being new, and being young, affords us one more beautiful freedom--to lighten up! 

We founded this company as friends and we have set out to find people who we will enjoy working with. Luckily for us, egg or chicken, enjoying work on this project and being passionate are paramount to our success. To make our site the best it can be, we have to put in a ton of hours, and to put in that time and do good work, you have to care about what you are doing and like the people you are working with. Even if you are only getting involved in a limited capacity, we want to work with people who see the potential of what LoveGov could be and feel passionate about it--and who are pleasant company too. As said if you ever have any ideas or questions about anything about the project, from the low-level technical, to our abstract goals, to how we work together and communicate  daily, to what LoveGov will be 50 years from now, talk to any of us. I don't promise to agree with you, but we will listen and take into consideration your input on any topic--we want to work with smart, friendly people and let them innovate and contribute in every way they can.

If this all sounds dandy to you, read further.


********** GITHUB ************

https://github.com/maximusfowler/LoveGov

If you are reading this, than you probably have already cloned a copy of the project. But for future reference, and just in case, the project is stored at the above url.

Throughout this document, when referring to file paths, '/<somename>' will refer to a file 'somename' in the root of the git project (eg this file is at '/README.txt').


********** MEET DJANGO ************

https://www.djangoproject.com/

On our server we are currently running:

python 2.7.1
django 1.4

We rely on a lot of the django framework:
- django-wsgi (settings.py)
- models
- url.conf
- templates/views

If you are not familiar with django, you should probably read through some of the documentation, but looking through our project (and this readme) and getting to know the code is also a good way to learn.


********** DEPENDENCIES ************

Install all dependencies for the project. With setuptools it shouldn't be that bad. Tried to include some links to send you in the right direction.
http://pypi.python.org/pypi/setuptools

Django
https://www.djangoproject.com/
pip install Django

PIL imaging library
http://www.pythonware.com/products/pil/
pip install PIL

sorl-thumbnail	
http://thumbnail.sorl.net/installation.html
pip install sorl-thumbnail

django_facebook	
https://github.com/tschellenbach/Django-facebook
pip install django_facebook

memcached      
http://memcached.org/
https://wincent.com/wiki/Installing_memcached_1.4.1_on_Mac_OS_X_10.6_Snow_Leopar             

python-memcached
http://pypi.python.org/pypi/python-memcached/
pip install python-memcached

BeautifulSoup	
http://www.crummy.com/software/BeautifulSoup/
pip install BeautifulSoup
pip install beautifulsoup4

xlrd
http://pypi.python.org/pypi/xlrd
pip install xlrd

haystack (v2.X)
http://haystacksearch.org/
https://github.com/toastdriven/django-haystack/
pip install -e git+https://github.com/toastdriven/django-haystack.git@master#egg=django-haystack
* don't do this: 'pip install django-haystack' (v1.X)

whoosh
http://pypi.python.org/pypi/Whoosh/
pip install Whoosh

debug_toolbar
http://pypi.python.org/pypi/django-debug-toolbar
pip install django-debug-toolbar

sunlight
http://python-sunlight.readthedocs.org/en/latest/index.html
pip install sunlight

googlemaps
http://pypi.python.org/pypi/googlemaps/
pip install googlemaps

south
pip install South

oauth2
pip install oauth2

sass
gem install sass

httpagentparser
git clone https://github.com/shon/httpagentparser.git
then run "python setup.py install"

django-extensions
pip install django-extensions

python-boto django-storages
pip install django-storages
pip install boto
pip install django-s3-folder-storage

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


