from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import generate_password_hash, check_password_hash

db = SQLAlchemy()

# =======================
# ShowerType: e.g. Corner, Frontal, Bathtub Screen, CNC-Cut
# =======================
class ShowerType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    description = db.Column(db.Text)
    profit_margin = db.Column(db.Float, default=0.20)  # e.g. 0.20 means 20%
    vat_rate = db.Column(db.Float, default=0.18)       # e.g. 0.18 means 18%
    needs_custom_quote = db.Column(db.Boolean, default=False)
    image_path = db.Column(db.String(255))  # <-- Add this line for image support

    models = db.relationship('Model', backref='shower_type', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'profit_margin': self.profit_margin,
            'vat_rate': self.vat_rate,
            'needs_custom_quote': self.needs_custom_quote,
            'image_path': self.image_path,
        }

# =======================
# Model: Each shower type can have multiple models
# =======================
class Model(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String)
    image_path = db.Column(db.String)
    shower_type_id = db.Column(db.Integer, db.ForeignKey('shower_type.id'), nullable=False)

    glass_components = db.relationship('ModelGlassComponent', backref='model', lazy=True)
    hardware_components = db.relationship('ModelHardwareComponent', backref='model', lazy=True)
    seal_components = db.relationship('ModelSealComponent', backref='model', lazy=True)
    addons = db.relationship('Addon', backref='model', lazy=True)

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
            'seal_components': [sc.to_dict() for sc in self.seal_components],
            'addons': [a.to_dict() for a in self.addons],
        }

# =======================
# Glass, Hardware, Finish, Pricing Models
# =======================
class GlassType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    def to_dict(self): return {'id': self.id, 'name': self.name}

class GlassThickness(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    thickness_mm = db.Column(db.Integer, nullable=False, unique=True)
    def to_dict(self): return {'id': self.id, 'thickness_mm': self.thickness_mm}

class GlassPricing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    glass_type_id = db.Column(db.Integer, db.ForeignKey('glass_type.id'), nullable=False)
    thickness_id = db.Column(db.Integer, db.ForeignKey('glass_thickness.id'), nullable=False)
    price_per_m2 = db.Column(db.Float, nullable=False)
    __table_args__ = (db.UniqueConstraint('glass_type_id', 'thickness_id', name='_glass_type_thickness_uc'),)
    glass_type = db.relationship('GlassType')
    thickness = db.relationship('GlassThickness')
    def to_dict(self):
        return {
            'id': self.id,
            'glass_type_id': self.glass_type_id,
            'glass_type': self.glass_type.name if self.glass_type else None,
            'thickness_id': self.thickness_id,
            'thickness_mm': self.thickness.thickness_mm if self.thickness else None,
            'price_per_m2': self.price_per_m2
        }

class Finish(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    def to_dict(self): return {'id': self.id, 'name': self.name}

class HardwareType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    def to_dict(self): return {'id': self.id, 'name': self.name}

class HardwarePricing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hardware_type_id = db.Column(db.Integer, db.ForeignKey('hardware_type.id'), nullable=False)
    finish_id = db.Column(db.Integer, db.ForeignKey('finish.id'), nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    __table_args__ = (db.UniqueConstraint('hardware_type_id', 'finish_id', name='_hardware_type_finish_uc'),)
    hardware_type = db.relationship('HardwareType')
    finish = db.relationship('Finish')
    def to_dict(self):
        return {
            'id': self.id,
            'hardware_type_id': self.hardware_type_id,
            'hardware_type': self.hardware_type.name if self.hardware_type else None,
            'finish_id': self.finish_id,
            'finish': self.finish.name if self.finish else None,
            'unit_price': self.unit_price
        }

class SealType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    def to_dict(self): return {'id': self.id, 'name': self.name}

class SealPricing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seal_type_id = db.Column(db.Integer, db.ForeignKey('seal_type.id'))
    finish_id = db.Column(db.Integer, db.ForeignKey('finish.id'))
    unit_price = db.Column(db.Float)
    quantity = db.Column(db.Integer, default=1)
    seal_type = db.relationship('SealType')
    finish = db.relationship('Finish')
    def to_dict(self):
        return {
            "id": self.id,
            "seal_type_id": self.seal_type_id,
            "seal_type": self.seal_type.name if self.seal_type else "",
            "finish_id": self.finish_id,
            "finish": self.finish.name if self.finish else "",
            "unit_price": self.unit_price,
            "quantity": self.quantity
        }

# =======================
# Model component definitions (per model, per glass/hardware/seal)
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
            'glass_type_id': self.glass_type_id,
            'glass_type': self.glass_type.name if self.glass_type else None,
            'thickness_id': self.thickness_id,
            'thickness': self.thickness.thickness_mm if self.thickness else None,
            'quantity': self.quantity
        }

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
            'hardware_type_id': self.hardware_type_id,
            'hardware_type': self.hardware_type.name if self.hardware_type else None,
            'finish_id': self.finish_id,
            'finish': self.finish.name if self.finish else None,
            'quantity': self.quantity
        }

class ModelSealComponent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    model_id = db.Column(db.Integer, db.ForeignKey('model.id'), nullable=False)
    seal_type_id = db.Column(db.Integer, db.ForeignKey('seal_type.id'), nullable=False)
    finish_id = db.Column(db.Integer, db.ForeignKey('finish.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    seal_type = db.relationship('SealType')
    finish = db.relationship('Finish')
    def to_dict(self):
        return {
            'id': self.id,
            'seal_type_id': self.seal_type_id,
            'seal_type': self.seal_type.name if self.seal_type else None,
            'finish_id': self.finish_id,
            'finish': self.finish.name if self.finish else None,
            'quantity': self.quantity
        }

# =======================
# Admin, Addon, GalleryImage ... (unchanged)
# =======================

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    def set_password(self, password): self.password_hash = generate_password_hash(password)
    def check_password(self, password): return check_password_hash(self.password_hash, password)
    def to_dict(self): return {'id': self.id, 'username': self.username}

class Addon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    price = db.Column(db.Float, nullable=False)
    model_id = db.Column(db.Integer, db.ForeignKey('model.id'))
    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'price': self.price, 'model_id': self.model_id}

class GalleryImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    def to_dict(self):
        return {'id': self.id, 'image_path': self.image_path, 'description': self.description}