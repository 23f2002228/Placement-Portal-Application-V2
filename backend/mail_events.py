from html import escape

from email_utils import send_email


def try_send_email(*args, **kwargs):
    try:
        return send_email(*args, **kwargs)
    except Exception:
        return False


def format_value(value):
    if value is None:
        return "-"
    if hasattr(value, "strftime"):
        return value.strftime("%Y-%m-%d %H:%M")
    return str(value)


def html_message(title, lines):
    body = "".join(f"<p>{escape(str(line))}</p>" for line in lines if line)
    return f"<h2>{escape(title)}</h2>{body}"


def send_company_approval_email(company):
    if not company or not company.user:
        return False

    title = "Company registration approved"
    message = html_message(title, [
        f"Hello {company.hr_name},",
        f"{company.company_name} has been approved on the Placement Portal.",
        "You can now sign in, create placement drives, and manage applications.",
    ])

    return try_send_email(
        company.user.email,
        "Your company registration is approved",
        message,
        content="html",
    )


def send_company_rejection_email(company):
    if not company or not company.user:
        return False

    title = "Company registration rejected"
    message = html_message(title, [
        f"Hello {company.hr_name},",
        f"{company.company_name} could not be approved on the Placement Portal.",
        f"Reason: {company.rejection_reason or 'Not specified'}",
        "Please contact the placement office if you need clarification.",
    ])

    return try_send_email(
        company.user.email,
        "Your company registration was rejected",
        message,
        content="html",
    )


def send_interview_scheduled_email(application, interview):
    student = application.student if application else None
    user = student.user if student else None
    drive = application.drive if application else None
    company = drive.company if drive else None

    if not user or not drive:
        return False

    title = "Interview scheduled"
    message = html_message(title, [
        f"Hello {student.full_name},",
        f"Your interview for {drive.job_title} has been scheduled.",
        f"Company: {company.company_name if company else '-'}",
        f"Round: {interview.round_name or 'Interview'}",
        f"Time: {format_value(interview.scheduled_at)}",
        f"Mode: {interview.mode}",
        f"Venue or link: {interview.venue_or_link or '-'}",
    ])

    return try_send_email(
        user.email,
        f"Interview Scheduled - {drive.job_title}",
        message,
        content="html",
    )


def send_student_selected_email(application):
    student = application.student if application else None
    user = student.user if student else None
    drive = application.drive if application else None
    company = drive.company if drive else None
    placement = application.placement if application else None

    if not user or not drive:
        return False

    title = "Placement offer update"
    message = html_message(title, [
        f"Hello {student.full_name},",
        f"You have been selected for {drive.job_title}.",
        f"Company: {company.company_name if company else '-'}",
        f"Position: {placement.position if placement else drive.job_title}",
        f"Salary: {format_value(placement.salary if placement else drive.salary)}",
        "Please check the Placement Portal for your offer details.",
    ])

    return try_send_email(
        user.email,
        f"Selected - {drive.job_title}",
        message,
        content="html",
    )
