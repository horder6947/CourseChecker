import requests
from bs4 import BeautifulSoup
import os
import smtplib

URL = "https://mybanner.qu.edu.qa/PROD/bwckschd.p_disp_detail_sched?term_in=202510&crn_in="  # Replace with the actual URL
# crn = 14592
CHECK_INTERVAL = 2  # seconds

def send_email_notification():
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    your_email = "aaa75938167@gmail.com"
    your_password = "vhyletsszokihnlo"  # Use App Password for Gmail
    recipient_email = "kelrefaey00@gmail.com"

    subject = "Course Seat Available!"
    body = f"There are seats available! Check the course page: {URL}"

    message = f"Subject: {subject}\n\n{body}"

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(your_email, your_password)
            server.sendmail(your_email, recipient_email, message)
        print("✅ Email sent successfully.")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")


def get_remaining_seats(crn):
    response = requests.get(URL + str(crn))
    soup = BeautifulSoup(response.text, 'html.parser')

    table = soup.find('table', {'summary': 'This layout table is used to present the seating numbers.'})
    if not table:
        raise ValueError("Couldn't find the course seating table.")

    for row in table.find_all('tr'):
        label = row.find('span', string='Seats')
        if label:
            cells = row.find_all('td', class_='dddefault')
            if len(cells) >= 3:
                remaining = int(cells[2].get_text(strip=True))
                return remaining
            else:
                raise ValueError(f"Expected at least 3 <td> cells, found {len(cells)}.")

    raise ValueError("No row with label 'Seats' was found.")

def main():
    remaining = get_remaining_seats(14592)
    if remaining is not None and remaining > 0:
        print(f"Seats available: {remaining}")
        send_email_notification(remaining)
    else:
        print("No seats available.")

if __name__ == "__main__":
    main()

# print(get_seat_availability(14592))
