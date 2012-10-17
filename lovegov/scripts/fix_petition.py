from lovegov.frontend.views import *

m = getUser('Max Fowler')
p = Petition.objects.get(creator=m)

full_text = "This is a petition to protect freedom of information and the rights given to us by the first amendment. " \
"Blocking particular anti-piracy/freedom bills is not enough, this is a petition in support of all measures " \
"taken to ensure our freedom on the internet and oppose groups and legislation who seek to limit it. \n\n" \
"Bills like SOPA and PIPA are motivated by the media industries and are intended to ensure the protection " \
"of their intellectual property on the internet. Whatever your views on intellectual copyright and online piracy may be, " \
"what has concerned millions of conscientious citizens around the country, and even companies like Wikipedia, " \
"reddit and Mozilla (who all participated in a 'blackout' to oppose SOPA), is the way in which these same bills " \
"limit our freedom on the internet in general. \n\n" \
"Online banking, shopping, news, email, our social lives, politics! " \
"Our lives and our relationships with each other are becoming more and more intertwined with technology, and in " \
"particular the internet. So far the internet has been a remarkably free and self-regulated place, but it is only " \
"15 years old and it is still growing. If we do not fight to ensure that it stays free, then there are no " \
"guarantees that it will. If media companies are losing sales due to online piracy, they need to find solutions " \
"through new business models or distribution schemes--not draconian legislation which gives the government the " \
"power to regulate and control something which belongs to the people and should inherently be free. \n\n" \
"There are powerful groups which would like to pass legislation to more strictly regulate the internet, " \
"and the time is now to set the precedent that we will not let these powers win. " \
"Whether we accomplish this by defeating one ambiguous anti-piracy bill at a time, " \
"or passing a constitutional amendment to ensure the freedom of the internet for the future, " \
"sign this petition to recognize the importance of internet freedom and raise awareness that " \
"this is a freedom which needs to be protected."

p.full_text = full_text
p.save()