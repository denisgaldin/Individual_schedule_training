import pytest
import requests
import os
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL")


def get_headers_with_token(token):
    return {
        "Content-Type": "application/json",
        "User-Agent": "PostmanRuntime/7.44.1",
        "Platform": "IOS",
        "App-Version": "4.5.1",
        "token": token,
        "timezone": "Europe/Moscow"
    }


@pytest.mark.order(1)
def test_signup_and_cancel_training(access_token):
    headers = get_headers_with_token(access_token)

    club_guid = os.getenv("CLUB_GUID")
    hall_guid = os.getenv("HALL_GUID")
    subscription_guid = os.getenv("SUBSCRIPTION_GUID")

    list_url = f"{BASE_URL}/individualTrainingSchedule/clubs/{club_guid}/hall/{hall_guid}/list"
    resp_list = requests.get(list_url, headers=headers)
    scheduled_times = set()
    scheduled_guids = set()

    if resp_list.status_code == 200:
        trainings = resp_list.json().get("result", {}).get("list", [])
        for training in trainings:
            training_guid = training.get("trainingGuid")
            training_date = training.get("trainingDate")
            if training_guid and training_date:
                dt = datetime.fromisoformat(training_date.replace("Z", "+00:00"))
                formatted_date = dt.strftime("%Y-%m-%d %H:%M")
                scheduled_times.add(formatted_date)
                scheduled_guids.add(training_guid)

                cancel_url = f"{BASE_URL}/individualTrainingSchedule/clubs/{club_guid}/hall/{hall_guid}/cancel"
                cancel_resp = requests.post(cancel_url, headers=headers, json={"trainingGuid": training_guid})
                print(f"❌ Отменили тренировку {training_guid}: {cancel_resp.status_code} {cancel_resp.text}")
    else:
        print("⚠️ Не удалось получить список текущих тренировок")

    today = datetime.today()
    schedule_params = {
        "day": str(today.day).zfill(2),
        "month": str(today.month).zfill(2),
        "year": today.year
    }

    schedule_url = f"{BASE_URL}/clubs/{club_guid}/hall/{hall_guid}/schedule/list?" + urlencode(schedule_params)
    response_schedule = requests.get(schedule_url, headers=headers)
    assert response_schedule.status_code == 200, f"Ошибка получения расписания: {response_schedule.text}"

    schedule_data = response_schedule.json().get("result", {}).get("list", [])
    assert schedule_data, "Расписание пустое"

    MoscowTZ = timezone(timedelta(hours=3))
    now = datetime.now(MoscowTZ)

    available_classes = []

    for slot in schedule_data:
        slot_date_str = slot["date"].replace("Z", "+00:00")
        slot_dt = datetime.fromisoformat(slot_date_str)
        formatted_for_api = slot_dt.strftime("%Y-%m-%d %H:%M")

        if (
                slot.get("availablePlaces", 0) > 0 and
                slot_dt > now and
                formatted_for_api not in scheduled_times
        ):
            available_classes.append((slot, formatted_for_api))

    assert available_classes, "Нет доступных слотов для записи"

    chosen_slot = None
    for slot, training_date in available_classes:
        signup_payload = {
            "duration": slot["duration"],
            "subscriptionGuid": subscription_guid,
            "trainingDate": training_date
        }

        signup_url = f"{BASE_URL}/individualTrainingSchedule/clubs/{club_guid}/hall/{hall_guid}/signup/v2"
        response_signup = requests.post(signup_url, headers=headers, json=signup_payload)

        print(f"📨 Попытка записи на {training_date} → {response_signup.status_code}")
        print("➡️", response_signup.text)

        if response_signup.status_code == 200:
            print("✅ Успешная запись")
            chosen_slot = slot
            break
        elif "TRAINING_SIGNUP_FAIL" in response_signup.text:
            continue
        else:
            pytest.fail(f"Ошибка при записи: {response_signup.status_code} {response_signup.text}")

    assert chosen_slot, "❌ Не удалось записаться ни на один слот"
