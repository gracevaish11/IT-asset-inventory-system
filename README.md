# IT Asset Inventory System

A small, menu-driven Python console application for recording and managing
IT assets - laptops, desktops, servers, monitors, mobiles and tablets - backed
by a SQL database.

## What It Does

The program lets an IT department:

- record hardware details, operating system, and status for every device
- search the inventory by tag, manufacturer, model, serial number, OS,
  assigned user, department, or status
- update key fields (OS, status, assigned user, department, location, warranty)
- delete retired or incorrect records
- generate quick inventory reports (totals, by status, by type, by OS, by department)

## Technologies Used

```text
Python
SQLite
SQL
```

No web framework, no external dependencies, no internet connection required -
everything runs from the terminal.

## Project Structure

```text
IT_Asset_Inventory/
│
├── main.py            # Menu and application flow
├── database.py         # SQLite connection + table creation
├── asset_manager.py     # Add / view / search / update / delete logic
├── reports.py           # SQL COUNT()/GROUP BY reporting
├── requirements.txt
├── README.md
└── asset_inventory.db   # Created automatically on first run
```

## Database Structure

A single `assets` table:

| Column           | Type    | Notes                          |
|------------------|---------|---------------------------------|
| id               | INTEGER | Primary key, auto-increment     |
| asset_tag        | TEXT    | Required, must be unique        |
| asset_type       | TEXT    | Required (Laptop, Server, etc.) |
| manufacturer     | TEXT    |                                  |
| model            | TEXT    |                                  |
| serial_number    | TEXT    |                                  |
| operating_system | TEXT    |                                  |
| os_version       | TEXT    |                                  |
| status           | TEXT    | Active / Maintenance / Retired  |
| assigned_to      | TEXT    |                                  |
| department       | TEXT    |                                  |
| location         | TEXT    |                                  |
| purchase_date    | TEXT    | YYYY-MM-DD                      |
| warranty_expiry  | TEXT    | YYYY-MM-DD                      |

The database file and table are created automatically the first time you run
the program - there is nothing to set up manually.

## How to Run It

```bash
python main.py
```

No `pip install` is required - the project only uses Python's standard library.

On startup you'll see:

```text
========================================
       IT ASSET INVENTORY SYSTEM
========================================

1. Add Asset
2. View All Assets
3. Search Assets
4. Update Asset
5. Generate Reports
6. Delete Asset
7. Load Demo Data
8. Exit
```

The first time you run it, choose option **7** to load ~10 sample assets so
you have data to explore immediately. Loading demo data more than once will
never create duplicates.

## Main Features

- **Add Asset** - enter full hardware/OS/assignment details; asset tags are
  validated as required and unique before anything is written to the database.
- **View All Assets** - a clean, aligned console table of every asset.
- **Search Assets** - a single search term is matched with SQL `LIKE` across
  tag, manufacturer, model, serial number, OS, assigned user, department and
  status, so `Dell`, `Windows`, or `John` all return sensible results.
- **Update Asset** - look an asset up by ID or tag, see its current details,
  then update one field at a time (status is chosen from a numbered list).
- **Delete Asset** - look an asset up, view its details, then confirm before
  it's removed.
- **Generate Reports** - total asset count plus breakdowns by status, type,
  operating system and department, each built with SQL `COUNT()` / `GROUP BY`.

## Example Usage

```text
Enter your choice: 3
Enter search term: Dell

ID  Asset Tag  Type     Manufacturer  Model          OS       Status
1   LAP-001    Laptop   Dell          Latitude 5420  Windows  Active
5   DES-002    Desktop  Dell          OptiPlex 7010  Windows  Retired
6   SRV-001    Server   Dell          PowerEdge R740 Ubuntu   Active

3 asset(s) found.
```

```text
Enter your choice: 5

========================================
           INVENTORY REPORTS
========================================

Total Assets: 10

Assets by Status:
  Active     : 7
  Maintenance: 2
  Retired    : 1

Assets by Type:
  Laptop : 3
  Monitor: 2
  Desktop: 2
  Server : 1
  Mobile : 1
  Tablet : 1
```

## Security Notes

All SQL statements use parameterized queries (`?` placeholders) - user input
is never concatenated directly into a query string, which avoids SQL
injection even in this local, single-user tool.
