# NIUNIUŚ
This Django app is the website for the off-road club named "Niuniuś". 
The website consists of the home page and four subpages: about, blog, shop, and service station.
Blog and Shop subpages are ready to use, while About and Service Station are in progress and disabled for now.
![Main Page](niunius/static/niunius/img/readme_home.png)

In order to explore this project, you are very welcome to ***clone this repository*** to your local machine :)

After that, for start, follow the below steps:
1. create the virtual environment and run the command `pip install -r requirements.txt`
2. in the project directory create the file named ***local_settings.py*** and add there details for DATABASES configuration
3. run the command `python manage.py makemigrations` and then `python manage.py migrate`
4. initial data for database you may find in fixtures catalogue - load them to fully enjoy the website, run the command `python manage.py loaddata */fixtures/*.json`
5. finally run `python manage.py runserver` and have a good time!

