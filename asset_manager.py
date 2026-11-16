"""
asset_manager.py

Business logic for the IT Asset Inventory System:
adding, viewing, searching, updating and deleting assets,
plus demo data seeding. All SQL here uses parameterized
queries - user input is never concatenated into a query string.
"""

from database import get_connection

STATUSES = ["Active", "Maintenance", "Retired"]

# Fields a user is allowed to change through "Update Asset"
UPDATABLE_FIELDS = [
    ("operating_system", "Operating System"),
    ("os_version", "OS Version"),
    ("status", "Status"),
    ("assigned_to", "Assigned To"),
    ("department", "Department"),
    ("location", "Location"),
    ("warranty_expiry", "Warranty Expiry"),
]


# ---------------------------------------------------------------------------
# Add
# ---------------------------------------------------------------------------

def asset_tag_exists(asset_tag, conn=None):
    """Return True if an asset with this tag already exists."""
    own_conn = conn is None
    if own_conn:
        conn = get_connection()
    row = conn.execute(
        "SELECT id FROM assets WHERE asset_tag = ?", (asset_tag,)
    ).fetchone()
    if own_conn:
        conn.close()
    return row is not None


def add_asset(asset):
    """
    Insert a new asset. `asset` is a dict with keys matching the assets
    table columns (except id). Returns (success: bool, message: str).
    """
    conn = get_connection()

    if not asset.get("asset_tag"):
        conn.close()
        return False, "Asset Tag cannot be empty."

    if not asset.get("asset_type"):
        conn.close()
        return False, "Asset Type cannot be empty."

    if asset_tag_exists(asset["asset_tag"], conn):
        conn.close()
        return False, f"Asset Tag '{asset['asset_tag']}' is already in use."

    status = asset.get("status") or "Active"
    if status not in STATUSES:
        status = "Active"

    conn.execute(
        """
        INSERT INTO assets (
            asset_tag, asset_type, manufacturer, model, serial_number,
            operating_system, os_version, status, assigned_to,
            department, location, purchase_date, warranty_expiry
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            asset["asset_tag"], asset["asset_type"], asset.get("manufacturer", ""),
            asset.get("model", ""), asset.get("serial_number", ""),
            asset.get("operating_system", ""), asset.get("os_version", ""),
            status, asset.get("assigned_to", ""), asset.get("department", ""),
            asset.get("location", ""), asset.get("purchase_date", ""),
            asset.get("warranty_expiry", ""),
        ),
    )
    conn.commit()
    conn.close()
    return True, "Asset added successfully."


# ---------------------------------------------------------------------------
# View
# ---------------------------------------------------------------------------

def get_all_assets():
    """Return every asset, ordered by asset tag."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM assets ORDER BY asset_tag ASC").fetchall()
    conn.close()
    return rows


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

def search_assets(term):
    """
    Search across asset_tag, manufacturer, model, serial_number,
    operating_system, assigned_to, department and status using
    partial (LIKE) matching.
    """
    conn = get_connection()
    like_term = f"%{term}%"
    rows = conn.execute(
        """
        SELECT * FROM assets
        WHERE asset_tag LIKE ?
           OR manufacturer LIKE ?
           OR model LIKE ?
           OR serial_number LIKE ?
           OR operating_system LIKE ?
           OR assigned_to LIKE ?
           OR department LIKE ?
           OR status LIKE ?
        ORDER BY asset_tag ASC
        """,
        (like_term, like_term, like_term, like_term, like_term, like_term, like_term, like_term),
    ).fetchall()
    conn.close()
    return rows


def find_asset(identifier):
    """
    Look up a single asset by numeric ID or by asset tag.
    Returns the row, or None if nothing matches.
    """
    conn = get_connection()
    if identifier.isdigit():
        row = conn.execute(
            "SELECT * FROM assets WHERE id = ?", (int(identifier),)
        ).fetchone()
    else:
        row = conn.execute(
            "SELECT * FROM assets WHERE asset_tag = ?", (identifier,)
        ).fetchone()
    conn.close()
    return row


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------

def update_asset_field(asset_id, field, value):
    """Update a single column for one asset. `field` must be a known column."""
    allowed = {f for f, _ in UPDATABLE_FIELDS}
    if field not in allowed:
        return False, "That field cannot be updated."

    conn = get_connection()
    conn.execute(f"UPDATE assets SET {field} = ? WHERE id = ?", (value, asset_id))
    conn.commit()
    conn.close()
    return True, "Asset updated successfully."


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------

def delete_asset(asset_id):
    """Delete an asset by its numeric ID."""
    conn = get_connection()
    conn.execute("DELETE FROM assets WHERE id = ?", (asset_id,))
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Demo data
# ---------------------------------------------------------------------------

def seed_demo_data():
    """
    Insert ~10 realistic demo assets. Safe to run more than once -
    existing asset tags are skipped so no duplicates are created.
    Returns the number of records inserted.
    """
    demo_assets = [
        {"asset_tag": "LAP-001", "asset_type": "Laptop", "manufacturer": "Dell", "model": "Latitude 5420",
         "serial_number": "SN-LAT5420-01", "operating_system": "Windows", "os_version": "Windows 11 Pro",
         "status": "Active", "assigned_to": "John Smith", "department": "IT", "location": "Dublin",
         "purchase_date": "2023-02-10", "warranty_expiry": "2026-02-10"},
        {"asset_tag": "LAP-002", "asset_type": "Laptop", "manufacturer": "Lenovo", "model": "ThinkPad T14",
         "serial_number": "SN-TP14-02", "operating_system": "Windows", "os_version": "Windows 11 Pro",
         "status": "Active", "assigned_to": "Sarah Byrne", "department": "Finance", "location": "Dublin",
         "purchase_date": "2023-05-22", "warranty_expiry": "2026-05-22"},
        {"asset_tag": "LAP-003", "asset_type": "Laptop", "manufacturer": "Apple", "model": "MacBook Air M2",
         "serial_number": "SN-MBA-03", "operating_system": "macOS", "os_version": "Sonoma 14.4",
         "status": "Maintenance", "assigned_to": "Emma Walsh", "department": "Marketing", "location": "Cork",
         "purchase_date": "2022-11-01", "warranty_expiry": "2024-11-01"},
        {"asset_tag": "DES-001", "asset_type": "Desktop", "manufacturer": "HP", "model": "EliteDesk 800",
         "serial_number": "SN-ED800-01", "operating_system": "Windows", "os_version": "Windows 10 Pro",
         "status": "Active", "assigned_to": "Mark Kelly", "department": "IT", "location": "Dublin",
         "purchase_date": "2021-09-15", "warranty_expiry": "2024-09-15"},
        {"asset_tag": "DES-002", "asset_type": "Desktop", "manufacturer": "Dell", "model": "OptiPlex 7010",
         "serial_number": "SN-OP7010-02", "operating_system": "Windows", "os_version": "Windows 11 Pro",
         "status": "Retired", "assigned_to": "", "department": "Operations", "location": "Cork",
         "purchase_date": "2019-03-05", "warranty_expiry": "2022-03-05"},
        {"asset_tag": "SRV-001", "asset_type": "Server", "manufacturer": "Dell", "model": "PowerEdge R740",
         "serial_number": "SN-PER740-01", "operating_system": "Ubuntu", "os_version": "Ubuntu 22.04 LTS",
         "status": "Active", "assigned_to": "", "department": "IT", "location": "Dublin - Server Room",
         "purchase_date": "2022-06-18", "warranty_expiry": "2027-06-18"},
        {"asset_tag": "MON-001", "asset_type": "Monitor", "manufacturer": "Dell", "model": "P2422H",
         "serial_number": "SN-P2422H-01", "operating_system": "", "os_version": "",
         "status": "Active", "assigned_to": "John Smith", "department": "IT", "location": "Dublin",
         "purchase_date": "2023-02-10", "warranty_expiry": "2026-02-10"},
        {"asset_tag": "MON-002", "asset_type": "Monitor", "manufacturer": "LG", "model": "27UL500",
         "serial_number": "SN-27UL500-02", "operating_system": "", "os_version": "",
         "status": "Active", "assigned_to": "Sarah Byrne", "department": "Finance", "location": "Dublin",
         "purchase_date": "2023-05-22", "warranty_expiry": "2026-05-22"},
        {"asset_tag": "MOB-001", "asset_type": "Mobile", "manufacturer": "Apple", "model": "iPhone 13",
         "serial_number": "SN-IP13-01", "operating_system": "iOS", "os_version": "iOS 17.4",
         "status": "Active", "assigned_to": "Emma Walsh", "department": "Marketing", "location": "Cork",
         "purchase_date": "2022-08-30", "warranty_expiry": "2024-08-30"},
        {"asset_tag": "TAB-001", "asset_type": "Tablet", "manufacturer": "Microsoft", "model": "Surface Go 3",
         "serial_number": "SN-SG3-01", "operating_system": "Windows", "os_version": "Windows 11 Home",
         "status": "Maintenance", "assigned_to": "Mark Kelly", "department": "Sales", "location": "Dublin",
         "purchase_date": "2023-01-12", "warranty_expiry": "2025-01-12"},
    ]

    inserted = 0
    conn = get_connection()
    for asset in demo_assets:
        if asset_tag_exists(asset["asset_tag"], conn):
            continue
        conn.execute(
            """
            INSERT INTO assets (
                asset_tag, asset_type, manufacturer, model, serial_number,
                operating_system, os_version, status, assigned_to,
                department, location, purchase_date, warranty_expiry
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                asset["asset_tag"], asset["asset_type"], asset["manufacturer"], asset["model"],
                asset["serial_number"], asset["operating_system"], asset["os_version"],
                asset["status"], asset["assigned_to"], asset["department"], asset["location"],
                asset["purchase_date"], asset["warranty_expiry"],
            ),
        )
        inserted += 1
    conn.commit()
    conn.close()
    return inserted
