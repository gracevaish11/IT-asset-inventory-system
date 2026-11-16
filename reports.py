"""
reports.py

Reporting for the IT Asset Inventory System. Every report here is
built with a SQL COUNT() / GROUP BY query - no counting is done by
hand in Python.
"""

from database import get_connection


def print_reports():
    """Print all inventory reports to the console."""
    conn = get_connection()

    total = conn.execute("SELECT COUNT(*) AS c FROM assets").fetchone()["c"]

    print("\n" + "=" * 40)
    print("           INVENTORY REPORTS")
    print("=" * 40)

    print(f"\nTotal Assets: {total}")

    if total == 0:
        print("\nNo assets in the database yet.")
        conn.close()
        return

    _print_group_report(
        conn,
        title="Assets by Status",
        query="SELECT status AS label, COUNT(*) AS count FROM assets GROUP BY status ORDER BY count DESC",
    )

    _print_group_report(
        conn,
        title="Assets by Type",
        query="SELECT asset_type AS label, COUNT(*) AS count FROM assets GROUP BY asset_type ORDER BY count DESC",
    )

    _print_group_report(
        conn,
        title="Assets by Operating System",
        query="""
            SELECT COALESCE(NULLIF(operating_system, ''), 'Not Specified') AS label, COUNT(*) AS count
            FROM assets GROUP BY label ORDER BY count DESC
        """,
    )

    _print_group_report(
        conn,
        title="Assets by Department",
        query="""
            SELECT COALESCE(NULLIF(department, ''), 'Unassigned') AS label, COUNT(*) AS count
            FROM assets GROUP BY label ORDER BY count DESC
        """,
    )

    conn.close()


def _print_group_report(conn, title, query):
    rows = conn.execute(query).fetchall()
    print(f"\n{title}:")
    if not rows:
        print("  (no data)")
        return
    label_width = max(len(row["label"]) for row in rows) + 1
    for row in rows:
        print(f"  {row['label']:<{label_width}}: {row['count']}")
