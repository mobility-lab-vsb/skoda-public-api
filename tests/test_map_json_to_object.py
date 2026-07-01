from datetime import datetime
import json
import os
import sys
from typing import List, Optional
from pydantic import Field

current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(current_dir, "../src"))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from models.base_model import BaseModel
from models.common import VehicleError
from models.enums import (
    DoorsState,
    LockState,
    OnOffState,
    OpenCloseState,
    TemperatureUnit,
    YesNoState,
)
from models.vehicle import Odometer, VehicleObject, VehicleResponse
from models.vehicle_status import OverallVehicleStatus, VehicleStatus, VehicleStatusDetail


def load_test_json(filename: str = "vehicle_test.json") -> dict:
    file_path = os.path.join(current_dir, filename)
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

def run_test():
    print("Spouštím test parsování a mapování Škoda API JSONu ze souboru...")
    print("-" * 60)

    try:
        test_json_data = load_test_json("vehicle_test.json")

        response = VehicleResponse.model_validate(test_json_data)

        print("Data byla úspěšně napasována do objektů.")
        print("-" * 60)

        car = response.vehicle
        print(f"Model auta:{car.name}")
        print(f"VIN:{car.vin}")
        print(f"SPZ:{car.license_plate}")

        if car.odometer:
            print(f"Stav kilometrů: {car.odometer.mileage_in_km} km")

        if car.status:
            print(
                f"Zámky (Enum): {car.status.overall.doors_locked} (hodnota: {car.status.overall.doors_locked.value})"
            )
            print(f"Střešní okno: {car.status.detail.sunroof}")
            print(
                f"Čas pořízení dat: {car.status.car_captured_timestamp} (Typ: {type(car.status.car_captured_timestamp)})"
            )

        print("-" * 60)
        print(f"Počet chyb v logu: {len(response.errors)}")
        for i, error in enumerate(response.errors, 1):
            print(f"  Chyba #{i}: [{error.type}] - {error.description}")

    except FileNotFoundError:
        print(
            f"Soubor 'vehicle.json' nebyl nalezen v adresáři: {current_dir}"
        )
    except Exception as e:
        print(" Mapování dat selhalo.")
        print(e)


if __name__ == "__main__":
    run_test()