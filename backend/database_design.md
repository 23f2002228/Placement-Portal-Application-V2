# Database Design Document

## Project Name

**Placement Portal Application - V2**

## Database

The application uses **SQLite** as the database. Tables are created programmatically using Flask and SQLAlchemy models. The database follows a role-based structure with one unified user table and separate profile tables for students and companies.

## Design Approach

The system has three main roles:

```text
Admin
Company
Student
```

A single `users` table stores login credentials and role information for all users. Student-specific and company-specific details are stored in separate profile tables. Placement drives are created by companies and approved by the admin. Students apply to approved placement drives through the `applications` table.

---

## 1. Users Table

### Table Name

```text
users
```

### Purpose

Stores authentication and role information for all users: admin, company, and student.

### Fields

| Field | Type | Constraint | Description |
|---|---|---|---|
| id | Integer | Primary Key | Unique user ID |
| email | String | Unique, Not Null | Login email |
| password_hash | String | Not Null | Hashed password |
| role | String | Not Null | admin, company, or student |
| is_active | Boolean | Default True | Whether user account is active |
| is_blacklisted | Boolean | Default False | Whether user is blacklisted |
| created_at | DateTime | Default current time | Account creation time |
| updated_at | DateTime | Auto update | Last update time |

### Relationships

```text
users 1 -- 1 student_profiles
users 1 -- 1 company_profiles
users 1 -- many notifications
users 1 -- many application_status_history
```

---

## 2. Student Profiles Table

### Table Name

```text
student_profiles
```

### Purpose

Stores academic and personal details of students.

### Fields

| Field | Type | Constraint | Description |
|---|---|---|---|
| id | Integer | Primary Key | Unique student profile ID |
| user_id | Integer | Foreign Key, Unique, Not Null | References users.id |
| full_name | String | Not Null | Student name |
| roll_number | String | Unique, Not Null | Institute roll number |
| degree | String | Not Null | Student degree or programme |
| branch | String | Not Null | Student branch |
| year | Integer | Not Null | Current academic year |
| graduation_year | Integer | Not Null | Expected year of graduation |
| cgpa | Float | Not Null | Student CGPA |
| phone | String | Nullable | Contact number |
| resume_url | String | Nullable | Uploaded resume path |
| skills | Text | Nullable | Student skills |
| created_at | DateTime | Default current time | Profile creation time |
| updated_at | DateTime | Auto update | Last update time |

### Relationships

```text
student_profiles 1 -- 1 users
student_profiles 1 -- many applications
```

---

## 3. Company Profiles Table

### Table Name

```text
company_profiles
```

### Purpose

Stores company registration and approval details.

### Fields

| Field | Type | Constraint | Description |
|---|---|---|---|
| id | Integer | Primary Key | Unique company profile ID |
| user_id | Integer | Foreign Key, Unique, Not Null | References users.id |
| company_name | String | Not Null | Name of company |
| industry | String | Not Null | Company industry or sector |
| location | String | Not Null | Company location |
| hr_name | String | Not Null | HR representative name |
| hr_contact | String | Not Null | HR contact information |
| website | String | Nullable | Company website |
| description | Text | Nullable | Company description |
| approval_status | String | Default pending | pending, approved, rejected |
| rejection_reason | Text | Nullable | Reason for rejection |
| created_at | DateTime | Default current time | Registration time |
| updated_at | DateTime | Auto update | Last update time |

### Relationships

```text
company_profiles many -- 1 users
company_profiles 1 -- many placement_drives
company_profiles 1 -- many monthly_reports
```

---

## 4. Placement Drives / Job Positions Table

### Table Name

```text
placement_drives
```

### Purpose

Stores job positions and their associated recruitment drives created by companies.

### Fields

| Field | Type | Constraint | Description |
|---|---|---|---|
| id | Integer | Primary Key | Unique drive ID |
| company_id | Integer | Foreign Key, Not Null | References company_profiles.id |
| job_title | String | Not Null | Job title |
| job_description | Text | Not Null | Job description |
| location | String | Not Null | Job location |
| salary | Float | Not Null | Annual salary package |
| skills_required | Text | Not Null | Skills required for the position |
| employment_type | String | Not Null | Internship, full-time, etc. |
| min_cgpa | Float | Not Null | Minimum eligible CGPA |
| eligible_branches | Text | Not Null | JSON string of eligible branches |
| eligible_year | Integer | Not Null | Eligible academic year |
| application_deadline | DateTime | Not Null | Last date to apply |
| drive_date | DateTime | Nullable | Drive/interview date |
| status | String | Default pending | pending, approved, rejected, closed |
| rejection_reason | Text | Nullable | Reason for admin rejection |
| created_at | DateTime | Default current time | Drive creation time |
| updated_at | DateTime | Auto update | Last update time |

### Relationships

```text
placement_drives many -- 1 company_profiles
placement_drives 1 -- many applications
```

---

## 5. Applications Table

### Table Name

```text
applications
```

### Purpose

Stores records of students applying to placement drives.

### Fields

| Field | Type | Constraint | Description |
|---|---|---|---|
| id | Integer | Primary Key | Unique application ID |
| student_id | Integer | Foreign Key, Not Null | References student_profiles.id |
| drive_id | Integer | Foreign Key, Not Null | References placement_drives.id |
| application_date | DateTime | Default current time | Date of application |
| status | String | Default applied | applied, shortlisted, interview_scheduled, selected, rejected |
| remarks | Text | Nullable | Company/admin remarks |
| created_at | DateTime | Default current time | Creation time |
| updated_at | DateTime | Auto update | Last update time |

### Special Constraint

```text
UNIQUE(student_id, drive_id)
```

This prevents a student from applying to the same placement drive more than once.

### Relationships

```text
applications many -- 1 student_profiles
applications many -- 1 placement_drives
applications 1 -- many interviews
applications 1 -- many application_status_history
applications 1 -- zero or one placements
```

---

## 6. Placements Table

### Table Name

```text
placements
```

### Purpose

Stores the final placement or job offer created from a selected application.

### Fields

| Field | Type | Constraint | Description |
|---|---|---|---|
| id | Integer | Primary Key | Unique placement ID |
| application_id | Integer | Foreign Key, Unique, Not Null | References applications.id |
| position | String | Not Null | Offered position |
| salary | Float | Not Null | Offered annual salary |
| joining_date | Date | Nullable | Expected joining date |
| status | String | Default offered | offered, accepted, declined, joined |
| placed_at | DateTime | Default current time | Placement recorded time |
| created_at | DateTime | Default current time | Creation time |
| updated_at | DateTime | Auto update | Last update time |

### Special Constraints

```text
UNIQUE(application_id)
```

Student, drive, and company information is obtained through the placement's application. This prevents those values from contradicting the selected application.

### Relationships

```text
placements 1 -- 1 applications
applications 1 -- zero or one placements
```

---

## 7. Interviews Table

### Table Name

```text
interviews
```

### Purpose

Stores interview schedule and feedback details for applications.

### Fields

| Field | Type | Constraint | Description |
|---|---|---|---|
| id | Integer | Primary Key | Unique interview ID |
| application_id | Integer | Foreign Key, Not Null | References applications.id |
| scheduled_at | DateTime | Not Null | Interview date and time |
| mode | String | Not Null | online or offline |
| venue_or_link | String | Nullable | Interview venue or meeting link |
| round_name | String | Nullable | Technical, HR, coding round, etc. |
| status | String | Default scheduled | scheduled, completed, cancelled |
| feedback | Text | Nullable | Interview feedback |
| created_at | DateTime | Default current time | Creation time |

### Relationships

```text
interviews many -- 1 applications
```

---

## 8. Application Status History Table

### Table Name

```text
application_status_history
```

### Purpose

Maintains complete history of application status changes.

### Fields

| Field | Type | Constraint | Description |
|---|---|---|---|
| id | Integer | Primary Key | Unique history ID |
| application_id | Integer | Foreign Key, Not Null | References applications.id |
| changed_by_user_id | Integer | Foreign Key, Not Null | References users.id |
| old_status | String | Nullable | Previous application status |
| new_status | String | Not Null | Updated application status |
| note | Text | Nullable | Extra note |
| changed_at | DateTime | Default current time | Status change time |

### Relationships

```text
application_status_history many -- 1 applications
application_status_history many -- 1 users
```

### Special Constraints

Both `old_status` and `new_status` use the same allowed values as
`applications.status`. `old_status` may be null for the initial `applied`
history entry.

---

## 9. Notifications Table

### Table Name

```text
notifications
```

### Purpose

Stores user notifications for reminders, reports, exports, and system alerts.

### Fields

| Field | Type | Constraint | Description |
|---|---|---|---|
| id | Integer | Primary Key | Unique notification ID |
| user_id | Integer | Foreign Key, Not Null | References users.id |
| title | String | Not Null | Notification title |
| message | Text | Not Null | Notification message |
| notification_type | String | Default system | system, application_status, interview, approval, deadline, export, report |
| is_read | Boolean | Default False | Read/unread status |
| created_at | DateTime | Default current time | Notification time |

### Relationships

```text
notifications many -- 1 users
```

### Special Constraint

```text
notification_type IN (
    system,
    application_status,
    interview,
    approval,
    deadline,
    export,
    report
)
```

---

## 10. Export Jobs Table

### Table Name

```text
export_jobs
```

### Purpose

Tracks student- and company-triggered CSV export jobs.

### Fields

| Field | Type | Constraint | Description |
|---|---|---|---|
| id | Integer | Primary Key | Unique export job ID |
| requested_by_user_id | Integer | Foreign Key, Not Null | References users.id and identifies the requesting account |
| export_type | String | Not Null | application_history or placement_history |
| status | String | Default pending | pending, running, completed, failed |
| file_path | String | Nullable | Generated CSV file path |
| requested_at | DateTime | Default current time | Export request time |
| completed_at | DateTime | Nullable | Export completion time |
| error_message | Text | Nullable | Error details if failed |

### Relationships

```text
export_jobs many -- 1 users
```

### Special Constraints

```text
export_type IN (application_history, placement_history)
status IN (pending, running, completed, failed)
```

---

## 11. Monthly Reports Table

### Table Name

```text
monthly_reports
```

### Purpose

Stores generated monthly placement activity reports for companies.

### Fields

| Field | Type | Constraint | Description |
|---|---|---|---|
| id | Integer | Primary Key | Unique report ID |
| company_id | Integer | Foreign Key, Not Null | References company_profiles.id and identifies the reported company |
| month | Integer | Not Null | Report month |
| year | Integer | Not Null | Report year |
| total_drives | Integer | Default 0 | Number of drives conducted |
| total_applications | Integer | Default 0 | Number of applications |
| total_selected | Integer | Default 0 | Number of selected students |
| report_html_path | String | Nullable | HTML report file path |
| sent_to_company | Boolean | Default False | Whether the report was sent to the company |
| generated_at | DateTime | Default current time | Report generation time |

### Special Constraint

```text
UNIQUE(company_id, month, year)
```

This prevents duplicate monthly reports for the same company, month, and year.

### Relationships

```text
monthly_reports many -- 1 company_profiles
```

---

# Overall Relationship Summary

```text
User 1 -- 1 StudentProfile
User 1 -- 1 CompanyProfile
User 1 -- many Notification
User 1 -- many ApplicationStatusHistory
User 1 -- many ExportJob

CompanyProfile 1 -- many PlacementDrive
CompanyProfile 1 -- many MonthlyReport

StudentProfile 1 -- many Application
PlacementDrive 1 -- many Application

Application 1 -- many Interview
Application 1 -- many ApplicationStatusHistory
Application 1 -- zero or one Placement

StudentProfile 1 -- many ExportJob
```

---

# Main Many-to-Many Relationship

Students and placement drives have a many-to-many relationship.

```text
One student can apply to many placement drives.
One placement drive can receive applications from many students.
```

This is implemented using the `applications` table:

```text
student_profiles -- applications -- placement_drives
```

---

# Important Database Constraints

| Constraint | Purpose |
|---|---|
| `users.email UNIQUE` | Prevent duplicate login accounts |
| `student_profiles.user_id UNIQUE` | One user can have only one student profile |
| `company_profiles.user_id UNIQUE` | One user can have only one company profile |
| `student_profiles.roll_number UNIQUE` | Prevent duplicate student records |
| `applications UNIQUE(student_id, drive_id)` | Prevent duplicate applications |
| `placements.application_id UNIQUE` | One application can create only one placement |
| `monthly_reports UNIQUE(company_id, month, year)` | Prevent duplicate monthly reports for the same company |

---

# Suggested Table Creation Order

Create the models/tables in this order:

```text
1. users
2. student_profiles
3. company_profiles
4. placement_drives
5. applications
6. placements
7. interviews
8. application_status_history
9. notifications
10. export_jobs
11. monthly_reports
```

This order avoids foreign key dependency issues.

---

# ER Diagram Text Version

```text
+---------+
| users   |
+---------+
   | 1
   |------------------- 1
   |                     |
   v                     v
+------------------+   +------------------+
| student_profiles |   | company_profiles |
+------------------+   +------------------+
   | 1                    | 1
   |                      |
   v                      v
+--------------+      +------------------+
| applications | ---> | placement_drives |
+--------------+      +------------------+
   | 1
   |
   +------------------+
   |                  |
   v                  v
+------------+    +------------+
| interviews |    | placements |
+------------+    +------------+

applications 1 -- many application_status_history
users 1 -- many notifications
student_profiles 1 -- many export_jobs
```

---

# Conclusion

This database design supports all major requirements of the Placement Portal Application, including role-based login, student and company registration, admin approval, placement drive creation, student applications, eligibility checks, interview scheduling, application status tracking, daily reminders, monthly reports, and CSV export jobs.
