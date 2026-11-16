"""
main.py

IT Asset Inventory System - a menu-driven console application.

Run with:
    python main.py
"""

from database import init_db
import asset_manager
import reports

STATUSES = ["Active", "Maintenance", "Retired"]

ASSET_FIELDS = [
    ("asset_tag", "Asset Tag"),
    ("asset_type", "Asset Type"),
    ("manufacturer", "Manufacturer"),
    ("model", "Model"),
    ("serial_number", "Serial Number"),
    ("operating_system", "Operating System"),
    ("os_version", "OS Version"),
    ("status", "Status"),
    ("assigned_to", "Assigned To"),
    ("department", "Department"),
    ("location", "Location"),
    ("purchase_date", "Purchase Date"),
    ("warranty_expiry", "Warranty Expiry"),
]


def print_banner():
    print("=" * 40)
    print("       IT ASSET INVENTORY SYSTEM")
    print("=" * 40)


def print_menu():
    print("\n1. Add Asset")
    print("2. View All Assets")
    print("3. Search Assets")
    print("4. Update Asset")
    print("5. Generate Reports")
    print("6. Delete Asset")
    print("7. Load Demo Data")
    print("8. Exit")


def print_assets_table(rows):
    """Print a list of asset rows as an aligned console table."""
    if not rows:
        print("\nNo assets found.")
        return

    headers = ["ID", "Asset Tag", "Type", "Manufacturer", "Model", "OS", "Status"]
    data = []
    for r in rows:
        data.append([
            str(r["id"]), r["asset_tag"], r["asset_type"],
            r["manufacturer"] or "-", r["model"] or "-",
            r["operating_system"] or "-", r["status"],
        ])

    widths = [len(h) for h in headers]
    for row in data:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    def format_row(cells):
        return "  ".join(cell.ljust(widths[i]) for i, cell in enumerate(cells))

    print()
    print(format_row(headers))
    print("  ".join("-" * w for w in widths))
    for row in data:
        print(format_row(row))
    print(f"\n{len(rows)} asset(s) found.")


def print_asset_details(asset):
    print("\n" + "-" * 40)
    for field, label in ASSET_FIELDS:
        print(f"{label:<18}: {asset[field] or '-'}")
    print("-" * 40)


def prompt(label, required=False):
    while True:
        value = input(f"{label}: ").strip()
        if value or not required:
            return value
        print(f"{label} is required.")


# ---------------------------------------------------------------------------
# Menu actions
# ---------------------------------------------------------------------------

def action_add_asset():
    print("\n--- Add Asset ---")
    asset = {}
    asset["asset_tag"] = prompt("Asset Tag", required=True)
    asset["asset_type"] = prompt("Asset Type", required=True)
    asset["manufacturer"] = prompt("Manufacturer")
    asset["model"] = prompt("Model")
    asset["serial_number"] = prompt("Serial Number")
    asset["operating_system"] = prompt("Operating System")
    asset["os_version"] = prompt("OS Version")

    print(f"Status options: {', '.join(STATUSES)}")
    status = prompt("Status (default Active)")
    asset["status"] = status if status in STATUSES else "Active"

    asset["assigned_to"] = prompt("Assigned To")
    asset["department"] = prompt("Department")
    asset["location"] = prompt("Location")
    asset["purchase_date"] = prompt("Purchase Date (YYYY-MM-DD)")
    asset["warranty_expiry"] = prompt("Warranty Expiry (YYYY-MM-DD)")

    success, message = asset_manager.add_asset(asset)
    print(f"\n{message}")


def action_view_assets():
    print("\n--- All Assets ---")
    rows = asset_manager.get_all_assets()
    print_assets_table(rows)


def action_search_assets():
    print("\n--- Search Assets ---")
    term = input("Enter search term: ").strip()
    if not term:
        print("Search term cannot be empty.")
        return
    rows = asset_manager.search_assets(term)
    print_assets_table(rows)


def action_update_asset():
    print("\n--- Update Asset ---")
    identifier = input("Enter Asset ID or Asset Tag: ").strip()
    if not identifier:
        print("You must enter an ID or asset tag.")
        return

    asset = asset_manager.find_asset(identifier)
    if asset is None:
        print(f"No asset found matching '{identifier}'.")
        return

    print_asset_details(asset)

    print("\nWhich field would you like to update?")
    for i, (field, label) in enumerate(asset_manager.UPDATABLE_FIELDS, start=1):
        print(f"{i}. {label}")
    print("0. Cancel")

    choice = input("\nEnter your choice: ").strip()
    if not choice.isdigit() or choice == "0":
        print("Update cancelled.")
        return

    index = int(choice) - 1
    if index < 0 or index >= len(asset_manager.UPDATABLE_FIELDS):
        print("Invalid choice.")
        return

    field, label = asset_manager.UPDATABLE_FIELDS[index]

    if field == "status":
        print(f"\nCurrent Status: {asset['status']}")
        print("1. Active\n2. Maintenance\n3. Retired")
        status_choice = input("Enter new status: ").strip()
        status_map = {"1": "Active", "2": "Maintenance", "3": "Retired"}
        new_value = status_map.get(status_choice)
        if new_value is None:
            print("Invalid status choice. Update cancelled.")
            return
    else:
        print(f"\nCurrent {label}: {asset[field] or '-'}")
        new_value = input(f"Enter new {label}: ").strip()

    success, message = asset_manager.update_asset_field(asset["id"], field, new_value)
    print(f"\n{message}")


def action_delete_asset():
    print("\n--- Delete Asset ---")
    identifier = input("Enter Asset ID or Asset Tag: ").strip()
    if not identifier:
        print("You must enter an ID or asset tag.")
        return

    asset = asset_manager.find_asset(identifier)
    if asset is None:
        print(f"No asset found matching '{identifier}'.")
        return

    print_asset_details(asset)
    confirm = input("Are you sure you want to delete this asset? (y/n): ").strip().lower()
    if confirm == "y":
        asset_manager.delete_asset(asset["id"])
        print("Asset deleted successfully.")
    else:
        print("Delete cancelled.")


def action_load_demo_data():
    inserted = asset_manager.seed_demo_data()
    if inserted:
        print(f"\nLoaded {inserted} demo asset(s).")
    else:
        print("\nDemo data is already loaded - no duplicates were created.")


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def main():
    init_db()
    print_banner()

    actions = {
        "1": action_add_asset,
        "2": action_view_assets,
        "3": action_search_assets,
        "4": action_update_asset,
        "5": reports.print_reports,
        "6": action_delete_asset,
        "7": action_load_demo_data,
    }

    while True:
        print_menu()
        choice = input("\nEnter your choice: ").strip()

        if choice == "8":
            print("\nGoodbye!")
            break

        action = actions.get(choice)
        if action is None:
            print("\nInvalid choice. Please enter a number from 1 to 8.")
            continue

        action()


if __name__ == "__main__":
    main()
