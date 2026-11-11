# CampusConnect

**Campus Mapping and Facility Management** web system for **Palawan State University – Main Campus** (Tiniguiban Heights, Puerto Princesa City).

Students can find school buildings, offices, laboratories, and facilities on an interactive map, search for a room or office, get walking directions between buildings, and stay updated with campus events, announcements, and maintenance reports.

> Final Lab project – built with Django.

## GROUPMATES

-   CHARS GERAND P. ALMOCERA
-   ARIEL JOHN CORDOVEZ

## Features

- **Dashboard** with campus statistics, upcoming events, announcements, and recent maintenance reports
- **Interactive campus map** (Leaflet.js + OpenStreetMap) with a marker for every building
- **Search** a room, office, building, or facility and fly to its location on the map
- **Walking directions** between two buildings (external routing API)
- **CRUD pages** for 7 tables: Departments, Buildings, Rooms, Facilities, Events, Announcements, Maintenance Reports
- **RESTful API** (Django REST Framework) for all tables
- Login required to add, edit, or delete records (anyone can view)

## Tech Stack

| Part | Technology |
|---|---|
| Backend | Python, Django, Django REST Framework |
| Database | SQLite |
| Map | Leaflet.js + OpenStreetMap tiles |
| External API | OSRM walking-route service (hosted by FOSSGIS, based on OpenStreetMap data) |
| UI | Bootstrap 5 + Bootstrap Icons |

## Database Tables

`Profile` (users, with role), `Department`, `Building`, `Room`, `Facility`, `Event`, `Announcement`, `MaintenanceReport`

## How to Run (Windows)

You need **Python 3.10 or newer** and **Git**. An internet connection is required (map tiles, Bootstrap, and the routing API are loaded online).

**1. Clone the project**

```bash
git clone https://github.com/Tazz022003/campusconnect.git
cd campusconnect
```

**2. Create and activate a virtual environment**

```bash
python -m venv venv
venv\Scripts\activate
```

(macOS/Linux: `python3 -m venv venv` then `source venv/bin/activate`)

**3. Install the requirements**

```bash
pip install -r requirements.txt
```

**4. Create the database**

```bash
python manage.py migrate
```

**5. Create an admin account** (you will use this to log in)

```bash
python manage.py createsuperuser
```

**6. Load the campus data** (buildings, rooms, facilities, etc.)

```bash
python manage.py loaddata campus_data
```

If that file is missing or gives an error, use the sample data instead:

```bash
python manage.py seed_data
```

> The sample data uses approximate building positions. Log in, open the map, and drag the pins to the correct spots (see _Editing building locations_ below).

**7. Run the server**

```bash
python manage.py runserver
```

Open **http://127.0.0.1:8000/** in your browser.

## Pages

| URL | What it is |
|---|---|
| `/` | Dashboard |
| `/map/` | Interactive campus map, search, and walking directions |
| `/buildings/`, `/rooms/`, `/departments/`, `/facilities/`, `/events/`, `/announcements/`, `/reports/` | CRUD pages |
| `/api/` | REST API root (browsable) |
| `/admin/` | Django admin (also used for logging in for now) |

## REST API

All endpoints support `GET` for everyone; `POST`, `PUT`, `PATCH`, and `DELETE` need a logged-in user. Most support `?search=`.

| Endpoint | Description |
|---|---|
| `/api/buildings/` | Buildings (with latitude and longitude) |
| `/api/rooms/?search=lab` | Rooms and offices (search by room, building, or department) |
| `/api/facilities/` | Campus facilities |
| `/api/events/` | Campus events |
| `/api/announcements/` | Announcements |
| `/api/departments/` | Departments |
| `/api/reports/` | Maintenance reports |
| `/api/route/?from=<building_id>&to=<building_id>` | Walking route between two buildings (calls the external routing API) |

## Editing building locations

While logged in (for example through `/admin/`), open the map page and **drag a building's pin** to the correct place. The new position is saved automatically.

This is controlled by `EDIT_MODE` (and `SHOW_COORDS_ON_CLICK`) near the top of the script in `campus/templates/campus/map.html`. Set both to `false` for the final demo.

## Project Structure

```
campusconnect/
├── manage.py
├── requirements.txt
├── campusconnect/          # project settings and root urls
└── campus/
    ├── models.py           # database tables
    ├── serializers.py      # REST API serializers
    ├── views.py            # API viewsets and map page
    ├── crud.py             # CRUD pages for all tables
    ├── dashboard.py        # dashboard view
    ├── routing.py          # external routing API call
    ├── urls.py
    ├── fixtures/           # campus_data.json
    ├── management/commands/seed_data.py
    └── templates/campus/   # base, dashboard, map, and crud templates
```

## Troubleshooting

- **Map tiles do not load or show "Access blocked":** make sure you are online and hard refresh the page (Ctrl+Shift+R).
- **"Routing service unavailable":** the external routing service is temporarily down or you are offline. Try again later.
- **`loaddata` error about users:** run `createsuperuser` first (step 5), then load the data again.
- **Pins in the wrong place:** drag them to the right building while logged in.
- **Port already in use:** run `python manage.py runserver 8001` and open `http://127.0.0.1:8001/`.

## Credits

- Map data &copy; [OpenStreetMap](https://www.openstreetmap.org/copyright) contributors
- Walking routes by [OSRM](https://project-osrm.org/) (FOSSGIS routing server)
- [Leaflet](https://leafletjs.com/), [Bootstrap](https://getbootstrap.com/), [Django](https://www.djangoproject.com/)

TEsting 12213213213