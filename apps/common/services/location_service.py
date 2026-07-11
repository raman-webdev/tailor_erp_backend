import json
from pathlib import Path


class LocationService:
    _data = None

    CATEGORY_TYPES = {
        1: "Metropolitan City",
        2: "Sub-Metropolitan City",
        3: "Municipality",
        4: "Rural Municipality",
    }

    @classmethod
    def load_data(cls):
        """
        Load Nepal location data from JSON.
        The file is loaded only once and cached.
        """
        if cls._data is None:
            file_path = (
                Path(__file__)
                .resolve()
                .parent.parent
                / "constants"
                / "nepal_locations.json"
            )

            with open(file_path, "r", encoding="utf-8") as f:
                cls._data = json.load(f)

        return cls._data

    @classmethod
    def _get_municipalities(cls, district):
        """
        Normalize municipality data.

        Some districts store municipalities as a list:
            [
                {...},
                {...}
            ]

        Others store them as a dict:
            {
                "9": {...},
                "10": {...}
            }

        This method always returns a list.
        """
        municipalities = district.get("municipalities", [])

        if isinstance(municipalities, dict):
            return list(municipalities.values())

        return municipalities

    @classmethod
    def get_provinces(cls):
        data = cls.load_data()

        return [
            {
                "id": province["id"],
                "name": province["name"],
            }
            for province in data
        ]

    @classmethod
    def get_province(cls, province_id):
        data = cls.load_data()

        for province in data:
            if province["id"] == province_id:
                return {
                    "id": province["id"],
                    "name": province["name"],
                }

        return None

    @classmethod
    def get_districts(cls, province_id):
        data = cls.load_data()

        for province in data:
            if province["id"] == province_id:
                return [
                    {
                        "id": district["id"],
                        "name": district["name"],
                    }
                    for district in province["districts"]
                ]

        return []

    @classmethod
    def get_district(
        cls,
        province_id,
        district_id,
    ):
        data = cls.load_data()

        for province in data:
            if province["id"] != province_id:
                continue

            for district in province["districts"]:
                if district["id"] == district_id:
                    return {
                        "id": district["id"],
                        "name": district["name"],
                    }

        return None

    @classmethod
    def get_local_levels(
        cls,
        province_id,
        district_id,
    ):
        data = cls.load_data()

        for province in data:
            if province["id"] != province_id:
                continue

            for district in province["districts"]:
                if district["id"] != district_id:
                    continue

                municipalities = cls._get_municipalities(
                    district
                )

                return [
                    {
                        "id": local["id"],
                        "district_id": local["district_id"],
                        "name": local["name"],
                        "type": cls.CATEGORY_TYPES.get(
                            local["category_id"],
                            "Unknown",
                        ),
                        "wards": local.get("wards", []),
                        "website": local.get("website"),
                        "area_sq_km": local.get(
                            "area_sq_km"
                        ),
                    }
                    for local in municipalities
                ]

        return []

    @classmethod
    def get_local_level(
        cls,
        province_id,
        district_id,
        local_level_id,
    ):
        data = cls.load_data()

        for province in data:
            if province["id"] != province_id:
                continue

            for district in province["districts"]:
                if district["id"] != district_id:
                    continue

                municipalities = cls._get_municipalities(
                    district
                )

                for local in municipalities:
                    if local["id"] == local_level_id:
                        return {
                            "id": local["id"],
                            "district_id": local["district_id"],
                            "name": local["name"],
                            "type": cls.CATEGORY_TYPES.get(
                                local["category_id"],
                                "Unknown",
                            ),
                            "wards": local.get("wards", []),
                            "website": local.get("website"),
                            "area_sq_km": local.get(
                                "area_sq_km"
                            ),
                        }

        return None