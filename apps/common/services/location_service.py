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
    def _normalize_list(cls, value):
        """
        Convert dict -> list while leaving lists unchanged.
        """
        if isinstance(value, dict):
            return list(value.values())

        if isinstance(value, list):
            return value

        return []

    @classmethod
    def get_provinces(cls):
        provinces = cls._normalize_list(cls.load_data())

        return [
            {
                "id": province["id"],
                "name": province["name"],
            }
            for province in provinces
        ]

    @classmethod
    def get_province(cls, province_id):
        provinces = cls._normalize_list(cls.load_data())

        for province in provinces:
            if province["id"] == province_id:
                return {
                    "id": province["id"],
                    "name": province["name"],
                }

        return None

    @classmethod
    def get_districts(cls, province_id):
        provinces = cls._normalize_list(cls.load_data())

        for province in provinces:
            if province["id"] == province_id:

                districts = cls._normalize_list(
                    province.get("districts")
                )

                return [
                    {
                        "id": district["id"],
                        "name": district["name"],
                    }
                    for district in districts
                ]

        return []

    @classmethod
    def get_district(
        cls,
        province_id,
        district_id,
    ):
        provinces = cls._normalize_list(cls.load_data())

        for province in provinces:
            if province["id"] != province_id:
                continue

            districts = cls._normalize_list(
                province.get("districts")
            )

            for district in districts:
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
        provinces = cls._normalize_list(cls.load_data())

        for province in provinces:
            if province["id"] != province_id:
                continue

            districts = cls._normalize_list(
                province.get("districts")
            )


            for district in districts:
                if district["id"] != district_id:
                    continue

                municipalities = cls._normalize_list(
                    district.get("municipalities")
                )

                return [
                    {
                        "id": local.get("id"),
                        "district_id": local.get("district_id"),
                        "name": local.get("name"),
                        "type": cls.CATEGORY_TYPES.get(
                            local.get("category_id"),
                            "Unknown",
                        ),
                        "wards": local.get("wards", []),
                        "website": local.get("website"),
                        "area_sq_km": local.get("area_sq_km"),
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
        provinces = cls._normalize_list(cls.load_data())

        for province in provinces:
            if province["id"] != province_id:
                continue

            districts = cls._normalize_list(
                province.get("districts")
            )

            for district in districts:
                if district["id"] != district_id:
                    continue

                municipalities = cls._normalize_list(
                    district.get("municipalities")
                )

                for local in municipalities:
                    if local.get("id") == local_level_id:
                        return {
                            "id": local.get("id"),
                            "district_id": local.get("district_id"),
                            "name": local.get("name"),
                            "type": cls.CATEGORY_TYPES.get(
                                local.get("category_id"),
                                "Unknown",
                            ),
                            "wards": local.get("wards", []),
                            "website": local.get("website"),
                            "area_sq_km": local.get("area_sq_km"),
                        }

        return None