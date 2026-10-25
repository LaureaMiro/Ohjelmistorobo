from robocorp.tasks import task
from robocorp import browser, log
from dotenv import load_dotenv

import csv
import os
import smtplib
import ssl

from datetime import datetime
from email.message import EmailMessage


# True = luo raportti, mutta älä lähetä sähköpostia.
# False = luo raportti ja lähetä sähköposti.
TEST_MODE = False

load_dotenv()


@task
def student_task_manager():
    browser.configure(headless=False)

    os.makedirs("output", exist_ok=True)

    try:
        tasks = get_all_tasks()
        tasks = sort_tasks(tasks)

        report = save_tasks_as_csv(tasks)
        message = create_email_message(tasks)

    except Exception as error:
        message = (
            "Robotti tarvitsee apua.\n\n"
            "Tehtävien hakeminen tai raportin tekeminen epäonnistui.\n"
            "Tarkista verkkosivut ja tehtävien päivämäärät.\n\n"
            f"Virhe: {error}"
        )

        save_error(message)

        if not TEST_MODE:
            try:
                send_email("Robotti tarvitsee apua", message)
            except Exception:
                print("Myös virheilmoituksen lähettäminen epäonnistui.")

        raise

    if TEST_MODE:
        print("Testiajo valmis. Sähköpostia ei lähetetty.")
        print(message)

    else:
        try:
            send_email("Opiskelutehtävien raportti valmis", message, report)
            print("Sähköpostipalvelin hyväksyi viestin lähetettäväksi.")

        except Exception:
            save_error(
                "Raportti luotiin, mutta sähköpostin lähetys epäonnistui "
                "tai lähetyksen tila jäi epävarmaksi. "
                "Tarkista sähköpostiasetukset ja vastaanottajan postilaatikko."
            )
            raise RuntimeError(
                "Sähköpostin lähetys epäonnistui. Katso output/virhe.txt."
            ) from None


def get_all_tasks():
    websites = [
        "https://sacce656.github.io/Ohjelmistorobo/ohjelmistorobotiikka.html",
        "https://sacce656.github.io/Ohjelmistorobo/web-ohjelmointi.html",
        "https://sacce656.github.io/Ohjelmistorobo/tietokannat.html"
    ]

    all_tasks = []

    for website in websites:
        open_course_website(website)
        course_tasks = get_course_tasks()

        for row in course_tasks:
            all_tasks.append(row)

    return all_tasks


def open_course_website(website):
    browser.goto(website)


def get_course_tasks():
    page = browser.page()

    course = page.locator("#course-name").inner_text()
    page.locator("#tasks-body").wait_for()

    rows = page.locator("#tasks-body .task-row")

    if rows.count() == 0:
        raise ValueError(f"Kurssilta {course} ei löytynyt tehtäviä.")

    tasks = []

    for index in range(rows.count()):
        row = rows.nth(index)

        task_name = row.locator(".task-name").inner_text()
        deadline = row.locator(
            ".task-deadline time"
        ).get_attribute("datetime")
        status = row.locator(".task-status").inner_text()

        if not task_name or not deadline or not status:
            raise ValueError(f"Kurssilta {course} puuttuu tehtävän tietoja.")

        datetime.strptime(deadline, "%Y-%m-%d")

        task_data = {
            "Kurssi": course,
            "Tehtävä": task_name,
            "Palautuspäivä": deadline,
            "Tila": status
        }

        tasks.append(task_data)

    print(f"{course}: löytyi {len(tasks)} tehtävää.")

    return tasks


def get_deadline(row):
    return row["Palautuspäivä"]


def sort_tasks(tasks):
    return sorted(tasks, key=get_deadline)


def save_tasks_as_csv(tasks):
    report = "output/tehtavat.csv"

    columns = ["Kurssi", "Tehtävä", "Palautuspäivä", "Tila"]

    with open(report, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=columns,
            delimiter=";"
        )

        writer.writeheader()
        writer.writerows(tasks)

    print(f"Raportti tallennettu: {report}")

    return report


def create_email_message(tasks):
    message = "Hei!\n\n"
    message += "Robotti on saanut työnsä valmiiksi.\n"
    message += f"Kolmelta kurssisivulta löytyi {len(tasks)} tehtävää.\n"
    message += "Tehtävät on järjestetty palautuspäivän mukaan.\n\n"

    for row in tasks:
        message += f"Kurssi: {row['Kurssi']}\n"
        message += f"Tehtävä: {row['Tehtävä']}\n"
        message += f"Palautuspäivä: {row['Palautuspäivä']}\n"
        message += f"Tila: {row['Tila']}\n\n"

    message += "CSV-raportti on sähköpostin liitteenä.\n"

    with open("output/yhteenveto.txt", "w", encoding="utf-8") as file:
        file.write(message)

    return message

@log.suppress_variables()
def send_email(subject, message, attachment=None):
    sender = os.getenv("EMAIL_SENDER")
    password = os.getenv("EMAIL_PASSWORD")
    receiver = os.getenv("EMAIL_RECEIVER")

    if not sender or not password or not receiver:
        raise ValueError("Täytä sähköpostiasetukset .env-tiedostoon.")

    email = EmailMessage()
    email["From"] = sender
    email["To"] = receiver
    email["Subject"] = subject
    email.set_content(message)

    if attachment:
        with open(attachment, "rb") as file:
            email.add_attachment(
                file.read(),
                maintype="text",
                subtype="csv",
                filename="tehtavat.csv"
            )

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(
        "smtp.gmail.com",
        465,
        context=context,
        timeout=30
    ) as server:
        server.login(sender, password)
        server.send_message(email)


def save_error(message):
    with open("output/virhe.txt", "w", encoding="utf-8") as file:
        file.write(message)

    print(message)