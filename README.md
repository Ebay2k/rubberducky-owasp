# Installatie + Setup
Volg de onderstaande stappen om de applicatie lokaal te runnen.
1. **Clone de repository:**\
``git clone https://github.com/Rac-Software-Development/wp2-2025-mvc-1b3-rubberducky.git``
2.  **Maak een Virtual Environment:**\
``python -m venv .venv``
3. **Activate Virtual Environment:**
- Windows:
``.venv\Scripts\activate``
- macOS/Linux:
``. .venv/bin/activate``
4. **Installeer de requirements.txt:**\
``pip install -r requirements.txt``
5. **Start de applicatie:**\
``python app.py``

# Inloggegevens
### Administrator
- Email: ``admin@hub.com``
- Password: ``admin``

### Organization
- Email: ``org-ah@hub.com``
- Password: ``secret``

### Ervaringsdeskundigen

#### Sanne Jansen
- Email: ``sanne@example.com``
- Password: ``secret``

#### Jamal El Idrissi
- Email: ``jamal@example.com``
- Password: ``secret``

#### Lotte van Dijk
- Email: ``lotte@example.com``
- Password: ``secret``

### Screenshots
![img.png](Docs/img.png)\
![img_1.png](Docs/img_1.png)\
![img_2.png](Docs/img_2.png)\
![img_3.png](Docs/img_3.png)


### Bronnen
[Flask Tutorial Playlist](https://www.youtube.com/playlist?list=PL-osiE80TeTs4UjLw5MM6OjgkjFeUxCYH)\
[Flask Tutorial 2](https://www.youtube.com/watch?v=mqhxxeeTbu0)\
[Flexbox guide > navbar](https://css-tricks.com/snippets/css/a-guide-to-flexbox/)\
[Grid template colummns > responsive cards](https://css-tricks.com/snippets/css/complete-guide-grid/)\
[SQLite](https://www.youtube.com/watch?v=pd-0G0MigUA)\
[Flask Sessions](https://www.geeksforgeeks.org/python/how-to-use-flask-session-in-python-flask/)\
[Updating DB](https://www.youtube.com/watch?v=Wicjkn5_nIQ)\
[Forms](https://flask.palletsprojects.com/en/3.0.x/quickstart/#the-request-object)\
[Form validatie](https://developer.mozilla.org/en-US/docs/Learn/Forms/Form_validation)\
[Try Exception handling](https://www.w3schools.com/python/python_try_except.asp)


## AI Bronvermelding

![img_4.png](Docs/img_4.png)

![img_5.png](Docs/img_5.png)

![img_6.png](Docs/img_6.png)

### Flask werkte niet om onderzoeken te laten zien
### Conversatie<br/>
https://chatgpt.com/share/6968e47d-d54c-8009-99f7-9c2bdca41940

### Oplossing<br/>
In plaats van ```{{% for id in studies %}}``` moest ik ```{{% for study in studies %}}```<br/>
gebruiken om de loop werkend te krijgen.

### Waar heb ik de oplossing gebruikt?<br/>
Bestand<br/>
in ev-aanvragen.html.<br/><br/>
Code regel<br/>
Dit is inmiddels lijn 13 geworden.<br/><br/>
Git link<br/>
[Github link](https://github.com/Rac-Software-Development/wp2-2025-mvc-1b3-rubberducky/blob/main/templates/ev-aanvragen.html)

