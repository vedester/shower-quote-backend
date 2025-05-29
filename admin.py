from models import db, Admin
from flask import Flask

# Set up Flask app and DB (must match your main app config)
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shower_quote.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# ====== EDIT THESE ======
username = "admin"      # Change to your desired username
password = "admin123"   # Change to your desired password

with app.app_context():
    # Ensure the table exists
    db.create_all()

    # Check if admin already exists
    existing = Admin.query.filter_by(username=username).first()
    if existing:
        print(f"Admin user '{username}' already exists!")
    else:
        admin = Admin(username=username)
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        print(f"Admin user '{username}' created successfully!")

# =========================================
# You can expand this script to easily add
# other initial data for your new tables,
# such as GlassType, Finish, HardwareType,
# GlassThickness, SealType, etc.
#
# Example:
# from models import GlassType
# with app.app_context():
#     if not GlassType.query.filter_by(name="Clear").first():
#         db.session.add(GlassType(name="Clear"))
#         db.session.commit()
#         print("Initial GlassType 'Clear' added!")
# =========================================