from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import generate_password_hash, check_password_hash

db = SQLAlchemy()

# =======================
# ShowerType: Represents a type of shower (e.g., Handheld, Rainfall)
# =======================
class ShowerType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)

    # Relationship to Model (one-to-many)
    models = db.relationship('Model', backref='shower_type', lazy=True)

    def to_dict(self):
        return {'id': self.id, 'name': self.name}

# =======================
# Model: Represents a shower model/type (e.g., MTI-101)
# =======================
class Model(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    image_path = db.Column(db.String)
    shower_type_id = db.Column(db.Integer, db.ForeignKey('shower_type.id'), nullable=True)

    # Relationships with components
    glass_components = db.relationship('ModelGlassComponent', backref='model', lazy=True)
    hardware_components = db.relationship('ModelHardwareComponent', backref='model', lazy=True)
    seal_components = db.relationship('ModelSealComponent', backref='model', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'image_path': self.image_path,
            'shower_type_id': self.shower_type_id,
            'shower_type_name': self.shower_type.name if self.shower_type else None,
            'glass_components': [gc.to_dict() for gc in self.glass_components],
            'hardware_components': [hc.to_dict() for hc in self.hardware_components],
            'seal_components': [sc.to_dict() for sc in self.seal_components]
        }

# =======================
# GlassType: Represents a glass type (e.g., Clear, Frosted)
# =======================
class GlassType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

class GlassThickness(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    thickness_mm = db.Column(db.Integer, nullable=False)  # e.g. 6, 8, 10

class GlassPricing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    glass_type_id = db.Column(db.Integer, db.ForeignKey('glass_type.id'), nullable=False)
    thickness_id = db.Column(db.Integer, db.ForeignKey('glass_thickness.id'), nullable=False)
    price_per_m2 = db.Column(db.Float, nullable=False)

    glass_type = db.relationship('GlassType')
    thickness = db.relationship('GlassThickness')

# =======================
# Finish: Represents a hardware finish/material/color (e.g., Nickel, Gold)
# =======================
class Finish(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

# =======================
# HardwareType: e.g. Hinge, Handle, Wall Profile
# =======================
class HardwareType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

# =======================
# HardwarePricing: price for each hardware type + finish
# =======================
class HardwarePricing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hardware_type_id = db.Column(db.Integer, db.ForeignKey('hardware_type.id'), nullable=False)
    finish_id = db.Column(db.Integer, db.ForeignKey('finish.id'), nullable=False)
    unit_price = db.Column(db.Float, nullable=False)

    hardware_type = db.relationship('HardwareType')
    finish = db.relationship('Finish')

# =======================
# SealType: e.g. Side Seal, Balloon, Magnetic
# =======================
class SealType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

class SealPricing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seal_type_id = db.Column(db.Integer, db.ForeignKey('seal_type.id'), nullable=False)
    unit_price = db.Column(db.Float, nullable=False)

    seal_type = db.relationship('SealType')

# =======================
# ModelGlassComponent: Glass panel definition per model
# =======================
class ModelGlassComponent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    model_id = db.Column(db.Integer, db.ForeignKey('model.id'), nullable=False)
    glass_type_id = db.Column(db.Integer, db.ForeignKey('glass_type.id'), nullable=False)
    thickness_id = db.Column(db.Integer, db.ForeignKey('glass_thickness.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    glass_type = db.relationship('GlassType')
    thickness = db.relationship('GlassThickness')

    def to_dict(self):
        return {
            'id': self.id,
            'glass_type': self.glass_type.name if self.glass_type else None,
            'thickness': self.thickness.thickness_mm if self.thickness else None,
            'quantity': self.quantity
        }

# =======================
# ModelHardwareComponent: Hardware definition per model
# =======================
class ModelHardwareComponent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    model_id = db.Column(db.Integer, db.ForeignKey('model.id'), nullable=False)
    hardware_type_id = db.Column(db.Integer, db.ForeignKey('hardware_type.id'), nullable=False)
    finish_id = db.Column(db.Integer, db.ForeignKey('finish.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    hardware_type = db.relationship('HardwareType')
    finish = db.relationship('Finish')

    def to_dict(self):
        return {
            'id': self.id,
            'hardware_type': self.hardware_type.name if self.hardware_type else None,
            'finish': self.finish.name if self.finish else None,
            'quantity': self.quantity
        }

# =======================
# ModelSealComponent: Seal definition per model
# =======================
class ModelSealComponent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    model_id = db.Column(db.Integer, db.ForeignKey('model.id'), nullable=False)
    seal_type_id = db.Column(db.Integer, db.ForeignKey('seal_type.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    seal_type = db.relationship('SealType')

    def to_dict(self):
        return {
            'id': self.id,
            'seal_type': self.seal_type.name if self.seal_type else None,
            'quantity': self.quantity
        }

# =======================
# Addon: Represents add-ons/upgrades (optionally linked to a specific model)
# =======================
class Addon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    price = db.Column(db.Float, nullable=False)
    model_id = db.Column(db.Integer, db.ForeignKey('model.id'))

    model = db.relationship('Model')

# =======================
# GalleryImage: Stores image paths and descriptions for gallery
# =======================
class GalleryImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String, nullable=False)
    description = db.Column(db.String)

# =======================
# Admin: Stores admin credentials for authentication
# =======================
from werkzeug.security import generate_password_hash, check_password_hash

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)