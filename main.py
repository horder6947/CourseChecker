import requests
from bs4 import BeautifulSoup
import os
import smtplib
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

URL = os.environ['URL']  # Replace with the actual URL

matrix = [[15320, os.environ['RECIPIENT_EMAIL']],
          [12072, os.environ['RECIPIENT_EMAIL']]]

def send_email_notification(course_details: str, seats: int, index: int) -> None:
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    your_email = os.environ['SENDER_EMAIL']
    your_password = os.environ['PASSWORD']  # Use App Password for Gmail

    subject = f"Seat FOUND for {course_details}"

    html_body = f"""
    <html>
    <body>
        <h2 style="color: green;">✅ Seat Available!</h2>
        <p style="font-size: 18px;">
            <strong>{course_details}</strong><br><br>
            <span style="color: blue;">There are available seats for the course above!</span><br><br>
            <a href="https://ssr.qu.edu.qa/StudentRegistrationSsb/ssb/classRegistration/classRegistration" style="font-size: 18px;">Click here to register</a>
        </p>
    </body>
    </html>
    """

    # Set up MIME message
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = your_email
    msg["To"] = matrix[index][1]

    msg.attach(MIMEText(html_body, "html"))

    # Send the email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(your_email, your_password)

            server.sendmail(your_email, matrix[index][1], msg.as_string())

        print("✅ HTML email sent successfully to", matrix[index][1])
    except Exception as e:
        print(f"❌ Failed to send email: {e}")


def fetch_course_info(crn: int) -> tuple[int, str]:
    """
    Returns (remaining_seats, course_details_string)
    """
    resp  = requests.get(URL + str(crn), timeout=10)
    soup  = BeautifulSoup(resp.text, "html.parser")

    # (a) Course details  e.g. "Computer Ethics - 14592 - CMPS 200 - L03"
    th_tag = soup.find("th", class_="ddlabel", scope="row")
    course_details = th_tag.get_text(strip=True) if th_tag else f"CRN {crn}"

    # (b) Remaining seats
    table = soup.find("table", summary="This layout table is used to present the seating numbers.")
    remaining = 0
    if table:
        for row in table.find_all("tr"):
            if row.find("span", string="Seats"):
                cells = row.find_all("td", class_="dddefault")
                if len(cells) >= 3:
                    remaining = int(cells[2].get_text(strip=True))
                break

    return remaining, course_details

print("Looking for available seats for:")
for i in range(0, len(matrix)):
    print(matrix[i][0])
    
try:
    for i in range(0, len(matrix)):
        remaining, details = fetch_course_info(matrix[i][0])
        if remaining > 0:
            print(f"Found {remaining} available seat(s) for {details}")
            send_email_notification(details, remaining, i)
        else:
            print(f"No available seats for {details}")
except Exception as exc:
    print(f"⚠️ Error: {exc}")
