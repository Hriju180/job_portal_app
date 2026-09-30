# Placement Tracker

A full-stack job and placement tracking platform where recruiters post job openings and students apply, track application status, and manage their profiles through a 5-stage hiring pipeline.

**[Live Demo](#)** &nbsp;·&nbsp; **[Report Bug](https://github.com/Hriju180/job_portal_app/issues)** &nbsp;·&nbsp; **[Request Feature](https://github.com/Hriju180/job_portal_app/issues)**

---

## Table of Contents

- [About](#about)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Screenshots](#screenshots)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [API Endpoints](#api-endpoints)
- [Database Schema](#database-schema)
- [Project Structure](#project-structure)
- [Deployment](#deployment)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## About

**Placement Tracker** is a role-based web application built to simplify the campus placement process. It replaces scattered spreadsheets and email threads with a single platform where:

- **Students** discover jobs, apply with their resume, and track where each application stands.
- **Recruiters** post openings, review applicants, and move candidates through the hiring pipeline.
- **Admins** oversee users, jobs, and applications from a single dashboard.

This project was built as a portfolio piece to demonstrate full-stack development with Django REST Framework and React.

---

## Features

### Authentication & Authorization
- JWT-based authentication (access + refresh tokens)
- Role-based access control: `student`, `recruiter`, `admin`
- Password reset via email
- Protected routes on both frontend and backend

### For Students
- Browse, search, and filter jobs (by location, type, package, skills)
- Upload a PDF resume (validated by type and size)
- Apply to jobs with an optional cover note
- Track application status through a live pipeline
- Withdraw applications
- Personal dashboard with status counts

### For Recruiters
- Create, edit, and delete job posts (owner-only)
- View all applicants per job
- Update applicant status: **Applied → Shortlisted → Interview → Selected / Rejected**
- Company profile with logo and website

### General
- Responsive design (mobile + desktop)
- Paginated list endpoints
- Search and filter query params
- Object-level permissions (only owners can edit their own jobs)

---

## Tech Stack

### Backend
| Technology | Purpose |
|---|---|
| **Django 5.x** | Web framework |
| **Django REST Framework** | REST API |
| **PostgreSQL** | Relational database |
| **SimpleJWT** | JWT authentication |
| **django-filter** | Search, filter, ordering |
| **Pillow** | Image field support |
| **django-environ** | Environment-based config |

### Frontend
| Technology | Purpose |
|---|---|
| **React 18** | UI library |
| **Vite** | Build tool + dev server |
| **React Router** | Client-side routing |
| **Axios** | HTTP client |
| **Tailwind CSS** | Utility-first styling |

### Deployment
| Service | Purpose |
|---|---|
| **Render** | Django backend hosting |
| **Vercel** | React frontend hosting |
| **Neon** | Serverless PostgreSQL |

---

## Architecture

- Frontend and backend are **decoupled** — they communicate purely over REST APIs.
- Authentication uses **JWT** stored in `localStorage`. Every request attaches `Authorization: Bearer <access_token>`.
- Access tokens expire after 8 hours; refresh tokens after 30 days.

---

## Screenshots

> Add 4–6 screenshots of your app here once it's deployed.

### Job Listings
![Job Listings](docs/screenshots/job-list.png)

### Job Detail & Apply
![Job Detail](docs/screenshots/job-detail.png)

### Student Dashboard
![Student Dashboard](docs/screenshots/student-dashboard.png)

### Recruiter Dashboard
![Recruiter Dashboard](docs/screenshots/recruiter-dashboard.png)

### Profile & Resume Upload
![Profile](docs/screenshots/profile.png)

---

## Getting Started

Follow these steps to run the project locally.

### Prerequisites

Make sure you have installed:

- **Python 3.10+** — [Download](https://www.python.org/downloads/)
- **Node.js 20+** and npm — [Download](https://nodejs.org/)
- **PostgreSQL 14+** — [Download](https://www.postgresql.org/download/)
- **Git** — [Download](https://git-scm.com/)

Verify:

```bash
python --version   # 3.10 or higher
node --version     # v20 or higher
psql --version     # 14 or higher
