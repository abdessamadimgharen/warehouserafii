# Warehouse Management System

**Author:** Abdessamad Imgharen  
**Project:** Student Project – End of Formation  

A Django-based warehouse management system for managing products, stock movements, demands, and reports. This system allows multiple products per demand, tracks stock entrances and exits, generates factures, and provides daily stock reports with charts and PDF export.

---

## Features

- **Products**
  - Add, edit, and delete products.
  - Auto-calculate total price based on quantity and unit price.
  - Maintain supplier information and stock quantity.

- **Demands**
  - Create demands with multiple products.
  - Must include at least one product to submit.
  - Send demands via email.
  - Generate HTML and PDF factures.
  - View and delete previous demands with confirmation.

- **Stock Movements**
  - Track entrances and exits per product.
  - Only staff users can create exits.
  - View stock movements and current stock for each product.

- **Reports**
  - Send reports with optional attachments.
  - View report history and generate factures.
  - Delete reports with confirmation.

- **Daily Stock Reports**
  - Filter stock movements by date.
  - Export daily stock report to PDF.
  - Visual chart of daily stock entrances and exits.

- **Media & Static Files**
  - All factures (demands/reports) saved in `MEDIA_ROOT/factures/`.
  - Static files (CSS, JS, images) are in the `static/` folder.

## Installation & Setup

1. Go to the project root folder

cd path/to/warehouserafii


2. Create a virtual environment and activate it

python -m venv env

# Windows
.\env\Scripts\activate

# Linux / Mac
source env/bin/activate


3. Install dependencies

pip install -r requirements.txt


4. Go to the Django project folder (where manage.py is)

cd warehouse_project


5. Apply database migrations

python manage.py migrate


6. Create a superuser (admin account)

python manage.py createsuperuser


7. Run the development server

python manage.py runserver


8. Access the app

Open your browser and go to:
http://127.0.0.1:8000/


## Usage
* Products 

- Add products via the dashboard.

- Edit, delete, and see total price auto-calculated.

- Keep supplier info and stock quantity up to date.

* Demands

- Navigate to Demands → Create New Demand.

- Add multiple products using “Add Another Product”.

- Must include at least one product to submit.

- View, delete, or generate HTML/PDF facture.

* Stock Movements

- Add stock entrances/exits for products.

- Only staff users can create exits.

- View product movements and current stock.

* Reports

- Send reports with optional attachments.

- View report history and generate factures.

- Delete reports with confirmation.

* Daily Stock Reports

- Filter movements by date.

- Export PDF for record keeping.

- Visual chart shows entrances and exits per product.