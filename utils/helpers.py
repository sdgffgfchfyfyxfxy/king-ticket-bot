def format_ticket_display(ticket_id, title, status, date):
    status_icon = "🟢" if status == "Open" else "🔴"
    return f"{status_icon} #{ticket_id} - {title} [{status}] ({date})"
