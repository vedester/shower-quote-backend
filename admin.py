from models import (
    db, Admin, ShowerType, GlassType, Finish, HardwareType, GlassThickness, SealType,
    HardwarePricing, SealPricing, GlassPricing, Model, ModelGlassComponent, ModelHardwareComponent, ModelSealComponent
)
from flask import Flask
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///shower_quote.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def create_admin_user(username, password):
    with app.app_context():
        db.create_all()
        if Admin.query.filter_by(username=username).first():
            print(f"Admin user '{username}' already exists!")
        else:
            admin = Admin(username=username)
            admin.set_password(password)
            db.session.add(admin)
            db.session.commit()
            print(f"Admin user '{username}' created successfully!")

def seed_if_missing(Model, field, values, extra_fields=None):
    with app.app_context():
        for value in values:
            exists = Model.query.filter(getattr(Model, field) == value).first()
            kwargs = {field: value}
            if extra_fields: kwargs.update(extra_fields)
            if not exists:
                db.session.add(Model(**kwargs))
                print(f"{Model.__name__} '{value}' added!")
        db.session.commit()
        print(f"{Model.__name__}s seeded successfully!")

def get_or_create(session, Model, **kwargs):
    if 'name' in kwargs:
        instance = session.query(Model).filter_by(name=kwargs['name']).first()
    else:
        instance = session.query(Model).filter_by(**kwargs).first()
    if not instance:
        instance = Model(**kwargs)
        session.add(instance)
        session.commit()
    return instance

def seed_hardware_pricing():
    with app.app_context():
        hardware_types = ["Hardware Type 1", "Hardware Type 2", "Hardware Type 3"]
        finishes = ["Black", "Gold", "Nickel", "White", "Rose Gold", "Graphite", "Chrome"]
        prices = [
            [80, 86, 79, 111, 82, 84, 79],
            [111, 61, 117, 107, 91, 72, 75],
            [95, 110, 59, 56, 69, 56, 109],
        ]
        for i, hw_type in enumerate(hardware_types):
            hw = get_or_create(db.session, HardwareType, name=hw_type)
            for j, finish_name in enumerate(finishes):
                finish = get_or_create(db.session, Finish, name=finish_name)
                price = prices[i][j]
                exists = HardwarePricing.query.filter_by(hardware_type_id=hw.id, finish_id=finish.id).first()
                if not exists:
                    db.session.add(HardwarePricing(
                        hardware_type_id=hw.id,
                        finish_id=finish.id,
                        unit_price=price
                    ))
                    print(f"HardwarePricing: {hw_type} / {finish_name} = {price}")
        db.session.commit()
        print("Hardware pricing seeded successfully!")

def seed_glass_pricing():
    with app.app_context():
        glass_types = ["Clear", "Frosted", "Tempered", "Tinted"]
        thicknesses = [6, 8, 10, 12]
        base_price = 100
        for i, glass_type_name in enumerate(glass_types):
            glass_type = get_or_create(db.session, GlassType, name=glass_type_name)
            for j, thickness_mm in enumerate(thicknesses):
                thickness = get_or_create(db.session, GlassThickness, thickness_mm=thickness_mm)
                price = base_price + i * 10 + j * 5
                exists = db.session.query(GlassPricing).filter_by(
                    glass_type_id=glass_type.id,
                    thickness_id=thickness.id
                ).first()
                if not exists:
                    db.session.add(GlassPricing(
                        glass_type_id=glass_type.id,
                        thickness_id=thickness.id,
                        price_per_m2=price
                    ))
                    print(f"GlassPricing: {glass_type_name} / {thickness_mm}mm = {price}")
        db.session.commit()
        print("Glass pricing seeded successfully!")

def seed_demo_model_with_components():
    with app.app_context():
        # Create a demo shower type with config, filter only by unique 'name'
        shower_type = get_or_create(db.session, ShowerType,
            name="Demo ShowerType"
        )
        # Optionally update config fields if needed
        shower_type.description = "A demo shower type for testing"
        shower_type.profit_margin = 0.2
        shower_type.vat_rate = 0.18
        shower_type.needs_custom_quote = False
        # Optionally set a demo image
        shower_type.image_path = "demo_showertype.jpg"
        db.session.commit()

        # Create a demo model
        model = Model.query.filter_by(name="Demo Model 1").first()
        if not model:
            model = Model(
                name="Demo Model 1",
                description="A sample model for testing",
                image_path="demo_model_1.jpg",
                shower_type_id=shower_type.id
            )
            db.session.add(model)
            db.session.commit()
            print("Demo Model 1 created.")

        # Glass component
        glass_type = GlassType.query.first()
        thickness = GlassThickness.query.first()
        if glass_type and thickness and not ModelGlassComponent.query.filter_by(model_id=model.id).first():
            db.session.add(ModelGlassComponent(
                model_id=model.id,
                glass_type_id=glass_type.id,
                thickness_id=thickness.id,
                quantity=2
            ))
            print("Glass component added to Demo Model 1.")

        # Hardware component
        hardware_type = HardwareType.query.first()
        finish = Finish.query.filter_by(name="Chrome").first()
        if hardware_type and finish and not ModelHardwareComponent.query.filter_by(model_id=model.id).first():
            db.session.add(ModelHardwareComponent(
                model_id=model.id,
                hardware_type_id=hardware_type.id,
                finish_id=finish.id,
                quantity=3
            ))
            print("Hardware component added to Demo Model 1.")

        # Seal component
        seal_type = SealType.query.first()
        seal_finish = Finish.query.filter_by(name="Black").first()
        if seal_type and seal_finish and not ModelSealComponent.query.filter_by(model_id=model.id).first():
            db.session.add(ModelSealComponent(
                model_id=model.id,
                seal_type_id=seal_type.id,
                finish_id=seal_finish.id,
                quantity=4
            ))
            print("Seal component added to Demo Model 1.")

        db.session.commit()
        print("Demo Model 1 components seeded successfully!")

if __name__ == "__main__":
    admin_username = os.getenv('ADMIN_USERNAME', 'admin')
    admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
    create_admin_user(admin_username, admin_password)

    # Shower types: demo with config
    seed_if_missing(
        ShowerType, 'name',
        ["Demo ShowerType", "Corner Shower", "Frontal Shower", "Bathtub Screen", "CNC-Cut Shower"],
        extra_fields={
            "description": "",
            "profit_margin": 0.2,
            "vat_rate": 0.18,
            "needs_custom_quote": False,
            "image_path": None  # Add a default path or leave as None
        }
    )
    seed_if_missing(GlassType, 'name', ["Clear", "Frosted", "Tempered", "Tinted"])
    all_finishes = [
        "Chrome", "Brushed Nickel", "Matte Black", "Gold", "Black", "Nickel", "White",
        "Rose Gold", "Graphite", "Transparent", "Grey", "Beige"
    ]
    seed_if_missing(Finish, 'name', all_finishes)
    seed_if_missing(HardwareType, 'name', [
        "Hinge", "Handle", "Knob", "Channel",
        "Hardware Type 1", "Hardware Type 2", "Hardware Type 3"
    ])
    seed_if_missing(GlassThickness, 'thickness_mm', [6, 8, 10, 12])
    seed_if_missing(SealType, 'name', [
        "Straight Seal", "Angled Seal", "Bottom Seal",
        "Gasket Type 1", "Gasket Type 2", "Gasket Type 3", "Magnet"
    ])

    seed_hardware_pricing()
    seed_glass_pricing()
    seed_demo_model_with_components()
    print("\nDatabase initialization and seeding complete!")