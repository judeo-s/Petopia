from petopia import db
from sqlalchemy.sql import func


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    slug = db.Column(db.String(20), unique=True, nullable=False)
    products = db.relationship('Product', back_populates='category', cascade='all, delete, delete-orphan')

    def __str__(self):
        return self.name


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id', ondelete='CASCADE'), nullable=False, unique=False)
    category = db.relationship('Category', back_populates='products')
    name = db.Column(db.String(30), nullable=False, unique=True)
    slug = db.Column(db.String(300), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False, unique=False)
    how_to_maintain = db.Column(db.Text, nullable=True, unique=False)
    where_to_keep = db.Column(db.Text, nullable=True, unique=False)
    image = db.Column(db.String(128), nullable=True, unique=True)
    price = db.Column(db.Integer(), nullable=False, unique=False, default=1000)
    order_items = db.relationship('OrderItem', back_populates='products', cascade='all, delete, delete-orphan')

    def __repr__(self):
        return f'id: {self.id} - Name: {self.name} - Rs. {self.price}'


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(30), nullable=False, unique=False)
    email_address = db.Column(db.String(100), nullable=False, unique=False)
    city = db.Column(db.String(50), nullable=False, unique=False)
    postal_code = db.Column(db.Integer(), nullable=False, unique=False)
    state = db.Column(db.String(50), nullable=False, unique=False)
    phone_no = db.Column(db.Integer(), nullable=False, unique=False)
    nearest_landmark = db.Column(db.String(500), nullable=False, unique=False)
    created_at = db.Column(db.DateTime(timezone=True), unique=False, nullable=False, default=func.now())
    is_shipped = db.Column(db.Boolean, nullable=False, unique=False, default=False)
    items = db.relationship('OrderItem', back_populates='order', cascade='all, delete, delete-orphan')
    total_amount = db.Column(db.Integer(), nullable=False, unique=False)

    def __repr__(self):
        return self.full_name + ' - ' + self.email_address + ' - ' + self.created_at
    


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id', ondelete='CASCADE'), nullable=False, unique=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id', ondelete='CASCADE'), nullable=False, unique=False)
    products = db.relationship('Product', back_populates='order_items')
    quantity = db.Column(db.Integer(), nullable=False, unique=False)
    order = db.relationship('Order', back_populates='items')

    def __repr__(self):
        return f'Order id:{self.order_id} - Product: {self.products.name} - {self.order.created_at}'



class Cart(object):
    def __init__(self, session):
        self.session = session
        self.cart = session.get('cart', None)

        if not self.cart:
            cart = session['cart'] = {}
            self.cart = cart

    def __iter__(self):
        for pk in self.cart.keys():
            self.cart[str(pk)]['product'] = Product.query.filter_by(id=int(pk)).first()

        for item in self.cart.values():
            item['slug'] = item['product'].slug
            item['total_price'] = item['quantity'] * item['product'].price

            yield item

    def __len__(self):
        return sum(int(item['quantity']) for item in self.cart.values())
    
    def save(self):
        self.session['cart'] = self.cart
        self.session.modified = True

    def remove(self, pk):
        if pk in self.cart:
            del self.cart[pk]
        self.save()

    def clear(self):
        self.cart = {}
        self.save()

    def add_or_update(self, pk, quantity=1):

        if not pk in self.cart:
            self.cart[pk] = {'quantity': quantity, 'product_id': pk}

        else:
            self.cart[pk]['quantity'] += int(quantity)
            
            if self.cart[pk]['quantity'] == 0:
                self.remove(pk)

        self.save()

    def get_item(self, pk):
        if str(pk) in self.cart:
            return self.cart[str(pk)]
        return None
    
    def get_total_amount(self):
        for pk in self.cart.keys():
            self.cart[str(pk)]['product'] = Product.query.filter_by(id=pk).first()
            
        return sum(item['quantity']*item['product'].price for item in self.cart.values())
