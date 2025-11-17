# GearCheck

GearCheck is a FastAPI-based service for tracking production jobs, users, gear inventory, and the full history of check-outs/check-ins. It is designed to help a production company quickly know who has what equipment, flag damage or missing items, and keep a searchable history of every transaction.

## Features

- CRUD APIs for users, jobs, and inventory items
- Dedicated transaction endpoint for both check-outs and check-ins
- Tracks per-item condition notes, damage/missing flags, and optional photo URLs
- Maintains the latest assignment status for each item
- SQLite database for easy local development

## Getting Started

1. **Install dependencies**

   ```bash
   pip install -e .
   ```

2. **Run the API**

   ```bash
   uvicorn app.main:app --reload
   ```

3. **Explore the docs**

   Open [http://localhost:8000/docs](http://localhost:8000/docs) for interactive Swagger UI.

## Data Model Overview

### Users
- `id`, `name`, `email`, `role`, `phone`, `notes`

### Jobs
- `id`, `name`, `client_name`, `shoot_start_date`, `shoot_end_date`, `location`, `producer_id`, `status`

### Items
- `id`, `name`, `serial_number`, `category`, `status`, `default_condition`, `notes`, `current_assignment_user_id`

### Transactions & Transaction Items
- `transactions`: `id`, `type`, `job_id`, `user_id`, `assigned_to_user_id`, `timestamp`, `notes`
- `transaction_items`: `id`, `transaction_id`, `item_id`, `status_before`, `status_after`, `condition_notes`, `is_missing`, `is_damaged`, `photos`

Each transaction represents either a check-out or a check-in and generates a history entry for every item involved.

## Example Workflow

1. Create users (admins, producers, crew)
2. Add jobs and inventory items
3. Use `POST /transactions` with `type="check_out"` to check out gear to a user or job
4. Use `POST /transactions` with `type="check_in"` to return items and capture condition updates
5. Query `/transactions` or `/items` to audit history and status

## Testing

This repository currently provides API integration through FastAPI's automatic docs. Add automated tests with `pytest` as the system evolves.
