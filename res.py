import os
import requests
import datetime
import json
from pytz import timezone    
 
def get_access_token():
    """
    Calls the login endpoint and returns the access token.
    """
    url = os.environ["LOGIN_URL"]  # Pull login URL from GitHub Secrets
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ",
        "Host": os.environ["HOST"],  # Pull Host URL from GitHub Secrets
        "Content-Type": "application/json",
    }
    payload = {
        "Email": os.environ["USERNAME"],
        "password": os.environ["PASSWORD"]
    }
    resp = requests.post(url, headers=headers, json=payload)
    resp.raise_for_status()
    data = resp.json()
    
    # Extract token from the response
    token = data.get("accessToken") or data.get("token")
    if not token:
        raise ValueError(f"No access token found in login response: {data!r}")
    return token
 
def make_reservation(token, reservation_date):
    """
    Calls the addNewReservations endpoint to make the reservation for the specified date.
    """
    reservation_url = os.environ["RESERVATION_URL"]  # Pull reservation URL from GitHub Secrets
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ",
        "Host": os.environ["HOST"],  # Pull Host URL from GitHub Secrets
        "Origin": os.environ["ORIGIN"],  # Pull Origin URL from GitHub Secrets
        "Referer": os.environ["REFERER"],  # Pull Referer URL from GitHub Secrets
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "x-content-type-options": "nosniff",
        "x-xss-protection": "0",
        "sec-ch-ua": '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "x-access-token": token,  # Use the token returned from login
        "Content-Type": "application/json"
    }
    # Prepare the reservation payload for two time slots (AM & PM)
    user_id = os.environ["USER_ID"]
    desk_id = os.environ["DESK_ID"]
    payload = [
        {
            "timeslot": "AM",
            "user": user_id,  # User ID (adjust if needed)
            "desk": desk_id,  # Desk ID (adjust if needed)
            "reservationdate": reservation_date
        },
        {
            "timeslot": "PM",
            "user": user_id,  # User ID (adjust if needed)
            "desk": desk_id,  # Desk ID (adjust if needed)
            "reservationdate": reservation_date
        }
    ]
 
    resp = requests.post(reservation_url, headers=headers, json=payload)
    resp.raise_for_status()
    print(f"✅ Reservation successful for {reservation_date} (status {resp.status_code})")

def check_reservation(token, reservation_date):
    """
    Verify Reservation.
    """
    user_id = os.environ["USER_ID"]
    check_url = os.environ["CHECK_URL"] + user_id + "/" + reservation_date + "/AM/desk" # Pull reservation URL from GitHub Secrets
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ",
        "Host": os.environ["HOST"],  # Pull Host URL from GitHub Secrets
        "Origin": os.environ["ORIGIN"],  # Pull Origin URL from GitHub Secrets
        "Referer": os.environ["REFERER"],  # Pull Referer URL from GitHub Secrets
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "x-content-type-options": "nosniff",
        "x-xss-protection": "0",
        "sec-ch-ua": '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "x-access-token": token,  # Use the token returned from login
        "Content-Type": "application/json"
    }
 
    resp = requests.get(check_url, headers=headers)
    resp.raise_for_status()
    print(f"✅ Reservation status for {reservation_date} \n" + json.dumps(resp.json(), indent=4))
 
def main():
    span = os.environ["PERIOD"]
    today_utc = datetime.datetime.utcnow().date()
    target_date = today_utc + datetime.timedelta(days=int(span))
    reservation_date = target_date.isoformat()  # “YYYY-MM-DD”
 
    token = get_access_token()
    
    paris = timezone('Europe/Paris')
    sa_time = datetime.datetime.now(paris)
    print ("Paris time:" + sa_time)
 
    make_reservation(token, reservation_date)
    check_reservation(token, reservation_date)
 
if __name__ == "__main__":
    main()
