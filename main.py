from src.api.adapters import OpenSkyNominatimAdapter

if __name__ == "__main__":
    adapter = OpenSkyNominatimAdapter()
    print("Границы Испании:", adapter.get_country_bbox("Spain"))
    print("Самолётов над Испанией:", len(adapter.get_aeroplanes("Spain")))