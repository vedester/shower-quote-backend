from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
from models import (
    db, ShowerType, Model, GlassType, Finish, Addon, GalleryImage, Admin,
    GlassThickness, GlassPricing,
    HardwareType, HardwarePricing,
    SealType, SealPricing,
    ModelGlassComponent, ModelHardwareComponent, ModelSealComponent,
)
from werkzeug.utils import secure_filename
import os
from functools import wraps

# ==== Flask App Setup ====
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shower_quote.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'a72d56dddaccf4d95715146efe7fd93b49c0672a97a16eed482c9cf33bfc7344'  # Change this in production!
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024  # 4MB max upload size

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

db.init_app(app)
CORS(app, supports_credentials=True)  # To allow credentialed requests for session-based auth

# ==== Utility: Protect Admin Routes ====
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_id'):
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    return decorated_function

# ==== Home Route ====
@app.route("/")
def home():
    return jsonify({"message": "Flask backend is running!"})

# ==== AUTHENTICATION: Admin Login/Logout ====
@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    admin = Admin.query.filter_by(username=username).first()
    if admin and admin.check_password(password):
        session['admin_id'] = admin.id
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Invalid credentials"}), 401

@app.route("/api/logout", methods=["POST"])
def logout():
    session.pop('admin_id', None)
    return jsonify({"success": True})

# ==== SHOWER TYPES CRUD ====
@app.route("/api/shower-types", methods=["GET"])
def get_shower_types():
    types = ShowerType.query.all()
    return jsonify([t.to_dict() for t in types])

@app.route("/api/shower-types", methods=["POST"])
@admin_required
def create_shower_type():
    data = request.get_json()
    t = ShowerType(name=data["name"])
    db.session.add(t)
    db.session.commit()
    return jsonify(t.to_dict()), 201

@app.route("/api/shower-types/<int:id>", methods=["PUT"])
@admin_required
def update_shower_type(id):
    t = ShowerType.query.get_or_404(id)
    data = request.get_json()
    t.name = data["name"]
    db.session.commit()
    return jsonify(t.to_dict())

@app.route("/api/shower-types/<int:id>", methods=["DELETE"])
@admin_required
def delete_shower_type(id):
    t = ShowerType.query.get_or_404(id)
    db.session.delete(t)
    db.session.commit()
    return jsonify({"success": True})

# ==== MODELS CRUD ====
@app.route("/api/models", methods=["GET"])
def get_models():
    models = Model.query.all()
    return jsonify([m.to_dict() for m in models])

@app.route("/api/models", methods=["POST"])
@admin_required
def add_model():
    data = request.get_json()
    model = Model(
        name=data.get("name"),
        description=data.get("description"),
        image_path=data.get("image_path"),
        shower_type_id=data.get("shower_type_id")
    )
    db.session.add(model)
    db.session.commit()
    return jsonify({"success": True, "id": model.id})

@app.route("/api/models/<int:model_id>", methods=["PUT"])
@admin_required
def update_model(model_id):
    data = request.get_json()
    model = Model.query.get_or_404(model_id)
    model.name = data.get("name", model.name)
    model.description = data.get("description", model.description)
    model.image_path = data.get("image_path", model.image_path)
    if "shower_type_id" in data:
        model.shower_type_id = data.get("shower_type_id")
    db.session.commit()
    return jsonify({"success": True})

@app.route("/api/models/<int:model_id>", methods=["DELETE"])
@admin_required
def delete_model(model_id):
    model = Model.query.get_or_404(model_id)
    db.session.delete(model)
    db.session.commit()
    return jsonify({"success": True})

# ==== GLASS TYPES CRUD ====
@app.route("/api/glass-types", methods=["GET"])
def get_glass_types():
    glass_types = GlassType.query.all()
    return jsonify([{"id": g.id, "name": g.name} for g in glass_types])

@app.route("/api/glass-types", methods=["POST"])
@admin_required
def add_glass_type():
    data = request.get_json()
    glass_type = GlassType(name=data.get("name"))
    db.session.add(glass_type)
    db.session.commit()
    return jsonify({"success": True, "id": glass_type.id})

@app.route("/api/glass-types/<int:glass_type_id>", methods=["PUT"])
@admin_required
def update_glass_type(glass_type_id):
    data = request.get_json()
    glass_type = GlassType.query.get_or_404(glass_type_id)
    glass_type.name = data.get("name", glass_type.name)
    db.session.commit()
    return jsonify({"success": True})

@app.route("/api/glass-types/<int:glass_type_id>", methods=["DELETE"])
@admin_required
def delete_glass_type(glass_type_id):
    glass_type = GlassType.query.get_or_404(glass_type_id)
    db.session.delete(glass_type)
    db.session.commit()
    return jsonify({"success": True})

# ==== GLASS THICKNESS CRUD ====
@app.route("/api/glass-thickness", methods=["GET"])
def get_glass_thickness():
    thicknesses = GlassThickness.query.all()
    return jsonify([{"id": t.id, "thickness_mm": t.thickness_mm} for t in thicknesses])

@app.route("/api/glass-thickness", methods=["POST"])
@admin_required
def add_glass_thickness():
    data = request.get_json()
    thickness = GlassThickness(thickness_mm=data.get("thickness_mm"))
    db.session.add(thickness)
    db.session.commit()
    return jsonify({"success": True, "id": thickness.id})

@app.route("/api/glass-thickness/<int:thickness_id>", methods=["PUT"])
@admin_required
def update_glass_thickness(thickness_id):
    data = request.get_json()
    thickness = GlassThickness.query.get_or_404(thickness_id)
    thickness.thickness_mm = data.get("thickness_mm", thickness.thickness_mm)
    db.session.commit()
    return jsonify({"success": True})

@app.route("/api/glass-thickness/<int:thickness_id>", methods=["DELETE"])
@admin_required
def delete_glass_thickness(thickness_id):
    thickness = GlassThickness.query.get_or_404(thickness_id)
    db.session.delete(thickness)
    db.session.commit()
    return jsonify({"success": True})

# ==== GLASS PRICING CRUD ====
@app.route("/api/glass-pricing", methods=["GET"])
def get_glass_pricing():
    glass_pricing = GlassPricing.query.all()
    return jsonify([
        {
            "id": p.id,
            "glass_type_id": p.glass_type_id,
            "glass_type_name": p.glass_type.name,
            "thickness_id": p.thickness_id,
            "thickness_mm": p.thickness.thickness_mm,
            "price_per_m2": p.price_per_m2
        } for p in glass_pricing
    ])

@app.route("/api/glass-pricing", methods=["POST"])
@admin_required
def add_glass_pricing():
    data = request.get_json()
    price = GlassPricing(
        glass_type_id=data.get("glass_type_id"),
        thickness_id=data.get("thickness_id"),
        price_per_m2=data.get("price_per_m2")
    )
    db.session.add(price)
    db.session.commit()
    return jsonify({"success": True, "id": price.id})

@app.route("/api/glass-pricing/<int:price_id>", methods=["PUT"])
@admin_required
def update_glass_pricing(price_id):
    data = request.get_json()
    price = GlassPricing.query.get_or_404(price_id)
    price.glass_type_id = data.get("glass_type_id", price.glass_type_id)
    price.thickness_id = data.get("thickness_id", price.thickness_id)
    price.price_per_m2 = data.get("price_per_m2", price.price_per_m2)
    db.session.commit()
    return jsonify({"success": True})

@app.route("/api/glass-pricing/<int:price_id>", methods=["DELETE"])
@admin_required
def delete_glass_pricing(price_id):
    price = GlassPricing.query.get_or_404(price_id)
    db.session.delete(price)
    db.session.commit()
    return jsonify({"success": True})

# ==== FINISH CRUD ====
@app.route("/api/finishes", methods=["GET"])
def get_finishes():
    finishes = Finish.query.all()
    return jsonify([{"id": f.id, "name": f.name} for f in finishes])

@app.route("/api/finishes", methods=["POST"])
@admin_required
def add_finish():
    data = request.get_json()
    finish = Finish(name=data.get("name"))
    db.session.add(finish)
    db.session.commit()
    return jsonify({"success": True, "id": finish.id})

@app.route("/api/finishes/<int:finish_id>", methods=["PUT"])
@admin_required
def update_finish(finish_id):
    data = request.get_json()
    finish = Finish.query.get_or_404(finish_id)
    finish.name = data.get("name", finish.name)
    db.session.commit()
    return jsonify({"success": True})

@app.route("/api/finishes/<int:finish_id>", methods=["DELETE"])
@admin_required
def delete_finish(finish_id):
    finish = Finish.query.get_or_404(finish_id)
    db.session.delete(finish)
    db.session.commit()
    return jsonify({"success": True})

# ==== HARDWARE TYPES CRUD ====
@app.route("/api/hardware-types", methods=["GET"])
def get_hardware_types():
    types = HardwareType.query.all()
    return jsonify([{"id": t.id, "name": t.name} for t in types])

@app.route("/api/hardware-types", methods=["POST"])
@admin_required
def add_hardware_type():
    data = request.get_json()
    t = HardwareType(name=data.get("name"))
    db.session.add(t)
    db.session.commit()
    return jsonify({"success": True, "id": t.id})

@app.route("/api/hardware-types/<int:type_id>", methods=["PUT"])
@admin_required
def update_hardware_type(type_id):
    data = request.get_json()
    t = HardwareType.query.get_or_404(type_id)
    t.name = data.get("name", t.name)
    db.session.commit()
    return jsonify({"success": True})

@app.route("/api/hardware-types/<int:type_id>", methods=["DELETE"])
@admin_required
def delete_hardware_type(type_id):
    t = HardwareType.query.get_or_404(type_id)
    db.session.delete(t)
    db.session.commit()
    return jsonify({"success": True})

# ==== HARDWARE PRICING CRUD ====
@app.route("/api/hardware-pricing", methods=["GET"])
def get_hardware_pricing():
    pricing = HardwarePricing.query.all()
    return jsonify([
        {
            "id": p.id,
            "hardware_type_id": p.hardware_type_id,
            "hardware_type_name": p.hardware_type.name,
            "finish_id": p.finish_id,
            "finish_name": p.finish.name,
            "unit_price": p.unit_price
        } for p in pricing
    ])

@app.route("/api/hardware-pricing", methods=["POST"])
@admin_required
def add_hardware_pricing():
    data = request.get_json()
    price = HardwarePricing(
        hardware_type_id=data.get("hardware_type_id"),
        finish_id=data.get("finish_id"),
        unit_price=data.get("unit_price")
    )
    db.session.add(price)
    db.session.commit()
    return jsonify({"success": True, "id": price.id})

@app.route("/api/hardware-pricing/<int:price_id>", methods=["PUT"])
@admin_required
def update_hardware_pricing(price_id):
    data = request.get_json()
    price = HardwarePricing.query.get_or_404(price_id)
    price.hardware_type_id = data.get("hardware_type_id", price.hardware_type_id)
    price.finish_id = data.get("finish_id", price.finish_id)
    price.unit_price = data.get("unit_price", price.unit_price)
    db.session.commit()
    return jsonify({"success": True})

@app.route("/api/hardware-pricing/<int:price_id>", methods=["DELETE"])
@admin_required
def delete_hardware_pricing(price_id):
    price = HardwarePricing.query.get_or_404(price_id)
    db.session.delete(price)
    db.session.commit()
    return jsonify({"success": True})

# ==== SEAL TYPES CRUD ====
@app.route("/api/seal-types", methods=["GET"])
def get_seal_types():
    types = SealType.query.all()
    return jsonify([{"id": t.id, "name": t.name} for t in types])

@app.route("/api/seal-types", methods=["POST"])
@admin_required
def add_seal_type():
    data = request.get_json()
    t = SealType(name=data.get("name"))
    db.session.add(t)
    db.session.commit()
    return jsonify({"success": True, "id": t.id})

@app.route("/api/seal-types/<int:type_id>", methods=["PUT"])
@admin_required
def update_seal_type(type_id):
    data = request.get_json()
    t = SealType.query.get_or_404(type_id)
    t.name = data.get("name", t.name)
    db.session.commit()
    return jsonify({"success": True})

@app.route("/api/seal-types/<int:type_id>", methods=["DELETE"])
@admin_required
def delete_seal_type(type_id):
    t = SealType.query.get_or_404(type_id)
    db.session.delete(t)
    db.session.commit()
    return jsonify({"success": True})

# ==== SEAL PRICING CRUD ====
@app.route("/api/seal-pricing", methods=["GET"])
def get_seal_pricing():
    pricing = SealPricing.query.all()
    return jsonify([
        {
            "id": p.id,
            "seal_type_id": p.seal_type_id,
            "seal_type_name": p.seal_type.name,
            "unit_price": p.unit_price
        } for p in pricing
    ])

@app.route("/api/seal-pricing", methods=["POST"])
@admin_required
def add_seal_pricing():
    data = request.get_json()
    price = SealPricing(
        seal_type_id=data.get("seal_type_id"),
        unit_price=data.get("unit_price")
    )
    db.session.add(price)
    db.session.commit()
    return jsonify({"success": True, "id": price.id})

@app.route("/api/seal-pricing/<int:price_id>", methods=["PUT"])
@admin_required
def update_seal_pricing(price_id):
    data = request.get_json()
    price = SealPricing.query.get_or_404(price_id)
    price.seal_type_id = data.get("seal_type_id", price.seal_type_id)
    price.unit_price = data.get("unit_price", price.unit_price)
    db.session.commit()
    return jsonify({"success": True})

@app.route("/api/seal-pricing/<int:price_id>", methods=["DELETE"])
@admin_required
def delete_seal_pricing(price_id):
    price = SealPricing.query.get_or_404(price_id)
    db.session.delete(price)
    db.session.commit()
    return jsonify({"success": True})

# ==== MODEL COMPONENTS: GLASS, HARDWARE, SEAL ====
@app.route("/api/model-glass-components/<int:model_id>", methods=["GET"])
def get_model_glass_components(model_id):
    components = ModelGlassComponent.query.filter_by(model_id=model_id).all()
    return jsonify([c.to_dict() for c in components])

@app.route("/api/model-glass-components", methods=["POST"])
@admin_required
def add_model_glass_component():
    data = request.get_json()
    comp = ModelGlassComponent(
        model_id=data["model_id"],
        glass_type_id=data["glass_type_id"],
        thickness_id=data["thickness_id"],
        quantity=data.get("quantity", 1)
    )
    db.session.add(comp)
    db.session.commit()
    return jsonify({"success": True, "id": comp.id})

@app.route("/api/model-glass-components/<int:comp_id>", methods=["PUT"])
@admin_required
def update_model_glass_component(comp_id):
    data = request.get_json()
    comp = ModelGlassComponent.query.get_or_404(comp_id)
    comp.glass_type_id = data.get("glass_type_id", comp.glass_type_id)
    comp.thickness_id = data.get("thickness_id", comp.thickness_id)
    comp.quantity = data.get("quantity", comp.quantity)
    db.session.commit()
    return jsonify({"success": True})

@app.route("/api/model-glass-components/<int:comp_id>", methods=["DELETE"])
@admin_required
def delete_model_glass_component(comp_id):
    comp = ModelGlassComponent.query.get_or_404(comp_id)
    db.session.delete(comp)
    db.session.commit()
    return jsonify({"success": True})

@app.route("/api/model-hardware-components/<int:model_id>", methods=["GET"])
def get_model_hardware_components(model_id):
    components = ModelHardwareComponent.query.filter_by(model_id=model_id).all()
    return jsonify([c.to_dict() for c in components])

@app.route("/api/model-hardware-components", methods=["POST"])
@admin_required
def add_model_hardware_component():
    data = request.get_json()
    comp = ModelHardwareComponent(
        model_id=data["model_id"],
        hardware_type_id=data["hardware_type_id"],
        finish_id=data["finish_id"],
        quantity=data.get("quantity", 1)
    )
    db.session.add(comp)
    db.session.commit()
    return jsonify({"success": True, "id": comp.id})

@app.route("/api/model-hardware-components/<int:comp_id>", methods=["PUT"])
@admin_required
def update_model_hardware_component(comp_id):
    data = request.get_json()
    comp = ModelHardwareComponent.query.get_or_404(comp_id)
    comp.hardware_type_id = data.get("hardware_type_id", comp.hardware_type_id)
    comp.finish_id = data.get("finish_id", comp.finish_id)
    comp.quantity = data.get("quantity", comp.quantity)
    db.session.commit()
    return jsonify({"success": True})

@app.route("/api/model-hardware-components/<int:comp_id>", methods=["DELETE"])
@admin_required
def delete_model_hardware_component(comp_id):
    comp = ModelHardwareComponent.query.get_or_404(comp_id)
    db.session.delete(comp)
    db.session.commit()
    return jsonify({"success": True})

@app.route("/api/model-seal-components/<int:model_id>", methods=["GET"])
def get_model_seal_components(model_id):
    components = ModelSealComponent.query.filter_by(model_id=model_id).all()
    return jsonify([c.to_dict() for c in components])

@app.route("/api/model-seal-components", methods=["POST"])
@admin_required
def add_model_seal_component():
    data = request.get_json()
    comp = ModelSealComponent(
        model_id=data["model_id"],
        seal_type_id=data["seal_type_id"],
        quantity=data.get("quantity", 1)
    )
    db.session.add(comp)
    db.session.commit()
    return jsonify({"success": True, "id": comp.id})

@app.route("/api/model-seal-components/<int:comp_id>", methods=["PUT"])
@admin_required
def update_model_seal_component(comp_id):
    data = request.get_json()
    comp = ModelSealComponent.query.get_or_404(comp_id)
    comp.seal_type_id = data.get("seal_type_id", comp.seal_type_id)
    comp.quantity = data.get("quantity", comp.quantity)
    db.session.commit()
    return jsonify({"success": True})

@app.route("/api/model-seal-components/<int:comp_id>", methods=["DELETE"])
@admin_required
def delete_model_seal_component(comp_id):
    comp = ModelSealComponent.query.get_or_404(comp_id)
    db.session.delete(comp)
    db.session.commit()
    return jsonify({"success": True})

# ==== ADDONS CRUD ====
@app.route("/api/addons", methods=["GET"])
def get_addons():
    model_id = request.args.get('model_id')
    if model_id:
        addons = Addon.query.filter_by(model_id=model_id).all()
    else:
        addons = Addon.query.all()
    return jsonify([{"id": a.id, "name": a.name, "price": a.price, "model_id": a.model_id} for a in addons])

@app.route("/api/addons", methods=["POST"])
@admin_required
def add_addon():
    data = request.get_json()
    addon = Addon(
        name=data.get("name"),
        price=data.get("price"),
        model_id=data.get("model_id")
    )
    db.session.add(addon)
    db.session.commit()
    return jsonify({"success": True, "id": addon.id})

@app.route("/api/addons/<int:addon_id>", methods=["PUT"])
@admin_required
def update_addon(addon_id):
    data = request.get_json()
    addon = Addon.query.get_or_404(addon_id)
    addon.name = data.get("name", addon.name)
    addon.price = data.get("price", addon.price)
    addon.model_id = data.get("model_id", addon.model_id)
    db.session.commit()
    return jsonify({"success": True})

@app.route("/api/addons/<int:addon_id>", methods=["DELETE"])
@admin_required
def delete_addon(addon_id):
    addon = Addon.query.get_or_404(addon_id)
    db.session.delete(addon)
    db.session.commit()
    return jsonify({"success": True})

# ==== GALLERY CRUD ====
@app.route("/api/gallery", methods=["GET"])
def get_gallery():
    images = GalleryImage.query.all()
    return jsonify([
        {"id": img.id, "image_path": img.image_path, "description": img.description}
        for img in images
    ])

@app.route("/api/gallery", methods=["POST"])
@admin_required
def add_gallery_image():
    data = request.get_json()
    image = GalleryImage(
        image_path=data.get("image_path"),
        description=data.get("description")
    )
    db.session.add(image)
    db.session.commit()
    return jsonify({"success": True, "id": image.id})

@app.route("/api/gallery/<int:image_id>", methods=["PUT"])
@admin_required
def update_gallery_image(image_id):
    data = request.get_json()
    image = GalleryImage.query.get_or_404(image_id)
    image.image_path = data.get("image_path", image.image_path)
    image.description = data.get("description", image.description)
    db.session.commit()
    return jsonify({"success": True})

@app.route("/api/gallery/<int:image_id>", methods=["DELETE"])
@admin_required
def delete_gallery_image(image_id):
    image = GalleryImage.query.get_or_404(image_id)
    db.session.delete(image)
    db.session.commit()
    return jsonify({"success": True})

# ==== IMAGE UPLOAD ENDPOINT (for gallery and model images) ====
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/upload-image', methods=['POST'])
@admin_required
def upload_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        image_path = f"/uploads/{filename}"
        return jsonify({"success": True, "image_path": image_path})
    return jsonify({"error": "Invalid file type"}), 400

# Serve uploaded images (for development only, use static server in production)
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ==== PRICES ENDPOINT (for backward compatibility, return all pricing data) ====
@app.route("/api/prices", methods=["GET"])
def get_all_prices():
    # Aggregate all pricing for backward compatibility
    prices = {
        "glass": [
            {
                "id": p.id,
                "glass_type_id": p.glass_type_id,
                "glass_type_name": p.glass_type.name,
                "thickness_id": p.thickness_id,
                "thickness_mm": p.thickness.thickness_mm,
                "price_per_m2": p.price_per_m2
            } for p in GlassPricing.query.all()
        ],
        "hardware": [
            {
                "id": p.id,
                "hardware_type_id": p.hardware_type_id,
                "hardware_type_name": p.hardware_type.name,
                "finish_id": p.finish_id,
                "finish_name": p.finish.name,
                "unit_price": p.unit_price
            } for p in HardwarePricing.query.all()
        ],
        "seal": [
            {
                "id": p.id,
                "seal_type_id": p.seal_type_id,
                "seal_type_name": p.seal_type.name,
                "unit_price": p.unit_price
            } for p in SealPricing.query.all()
        ]
    }
    return jsonify(prices)

# ==== DB INIT ====
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

    