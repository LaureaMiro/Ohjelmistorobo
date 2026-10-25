STUDENT TASK MANAGER ROBOT – TESTISIVUSTO

1. Avaa koko student-task-manager-site-kansio VS Codessa.
2. Avaa index.html Live Server -lisäosalla (Open with Live Server).
3. Klikkaa yhtä kolmesta kurssista ja tarkista tehtävätaulukko.
4. Robotilla avaa etusivu, etsi #course-list a -linkit, käy kurssisivuilla,
   ja lue #course-name ja #tasks-table tbody tr -rivit.

Pysyvät selektorit:
- Etusivun kurssilinkit: #course-list a
- Kurssin nimi: #course-name
- Taulukon tehtävärivit: #tasks-table tbody tr
- Tehtävän tunniste: .task-id
- Tehtävän nimi: .task-name
- Deadline: .task-deadline time (datetime-attribuutti: YYYY-MM-DD)
- Tila: .task-status

Robotti voi kerätä rivit muotoon:
kurssi,tehtava_id,tehtava,deadline,tila

Sivut ovat täysin staattisia: ei kirjautumista, popup-ikkunoita, eikä JavaScript-latauksia.
Esimerkkitehtävät eivät ole oikeita kurssitehtäviä.

Student Task Manager Pyhton-koodi

`tasks.py` hakee tehtävät kolmelta kurssisivulta, järjestää ne palautuspäivän mukaan ja tallentaa CSV-raportin. Robotti lähettää yhteenvedon ja raportin sähköpostitse sekä ilmoittaa virheistä.

Sähköpostiasetukset:

Luo `.env` samaan kansioon kuin `tasks.py`:

EMAIL_SENDER=omaosoite@gmail.com
EMAIL_PASSWORD=googlen_sovellussalasana
EMAIL_RECEIVER=vastaanottajan_osoite


Käyttö:

Avaa projekti VS Codessa ja käynnistä robotti Sema4.ai:n kautta.

- `TEST_MODE = True`: luo raportti ilman sähköpostia.
- `TEST_MODE = False`: luo raportti ja lähetä sähköposti.

Raportti tallentuu `output`-kansioon.
