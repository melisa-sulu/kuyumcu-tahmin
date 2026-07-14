from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

# Flask uygulamasını başlat
app = Flask(__name__)

# Database konfigürasyonu
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jewelry_shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max 16MB upload

# Database nesnesi
db = SQLAlchemy(app)

# ===== DATABASE MODELLERİ =====

class Customer(db.Model):
    """Müşteri Modeli"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(100))
    address = db.Column(db.Text)
    created_date = db.Column(db.DateTime, default=datetime.now)
    
    # İlişkiler
    orders = db.relationship('Order', backref='customer', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Customer {self.name}>'


class JewelryProduct(db.Model):
    """Mücevher Ürün Modeli"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Halka, Bilezik, Kolye vb.
    category = db.Column(db.String(50), nullable=False)  # altın, gümüş, etc
    material = db.Column(db.String(50))  # 14K, 18K, 22K
    weight_grams = db.Column(db.Float)
    stone_type = db.Column(db.String(100))  # Elmas, Zirkon, vb.
    cost_price = db.Column(db.Float)  # Alış fiyatı
    selling_price = db.Column(db.Float)  # Satış fiyatı
    image_path = db.Column(db.String(255))
    stock_quantity = db.Column(db.Integer, default=1)
    created_date = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f'<Jewelry {self.name}>'


class Order(db.Model):
    """Sipariş Modeli"""
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('jewelry_product.id'))
    order_date = db.Column(db.DateTime, default=datetime.now)
    delivery_date = db.Column(db.DateTime)
    quantity = db.Column(db.Integer, default=1)
    total_price = db.Column(db.Float)
    status = db.Column(db.String(50), default='Beklemede')  # Beklemede, Hazırlanıyor, Hazır, Teslim Edildi
    payment_status = db.Column(db.String(50), default='Ödenmedi')  # Ödenmedi, Kısmi, Ödenmiş
    notes = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Order #{self.id}>'


class PriceLog(db.Model):
    """Piyasa Fiyat Kaydı"""
    id = db.Column(db.Integer, primary_key=True)
    material_type = db.Column(db.String(50), nullable=False)  # Altın, Gümüş
    price_per_gram = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f'<PriceLog {self.material_type} - {self.price_per_gram}₺>'


# ===== ROTALAR (PAGES) =====

@app.route('/')
def index():
    """Ana Sayfa"""
    total_customers = Customer.query.count()
    total_products = JewelryProduct.query.count()
    total_orders = Order.query.count()
    today_orders = Order.query.filter(
        Order.order_date >= datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    ).count()
    
    context = {
        'total_customers': total_customers,
        'total_products': total_products,
        'total_orders': total_orders,
        'today_orders': today_orders
    }
    
    return render_template('index.html', **context)


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    """Fiyat Tahmin Sayfası"""
    if request.method == 'POST':
        # TODO: Fotoğraf işleme ve ML modeli kodu gelecek
        return jsonify({'message': 'Model hazır değil henüz'})
    
    return render_template('predict.html')


@app.route('/customers')
def customers():
    """Müşteri Yönetimi"""
    all_customers = Customer.query.all()
    return render_template('customers.html', customers=all_customers)


@app.route('/add-customer', methods=['POST'])
def add_customer():
    """Müşteri Ekle"""
    data = request.json
    new_customer = Customer(
        name=data.get('name'),
        phone=data.get('phone'),
        email=data.get('email'),
        address=data.get('address')
    )
    db.session.add(new_customer)
    db.session.commit()
    return jsonify({'status': 'success', 'customer_id': new_customer.id})


@app.route('/inventory')
def inventory():
    """Envanter Yönetimi"""
    products = JewelryProduct.query.all()
    total_value = sum([p.selling_price * p.stock_quantity for p in products]) if products else 0
    return render_template('inventory.html', products=products, total_value=total_value)


@app.route('/analytics')
def analytics():
    """Analiz Sayfası"""
    return render_template('analytics.html')


# ===== HATA YÖNETİMİ =====

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('500.html'), 500


# ===== UYGULAMA BAŞLATMA =====

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Veritabanını oluştur
        print("✅ Veritabanı hazırlandı!")
    
        app.run(debug=True, host='0.0.0.0', port=8000)