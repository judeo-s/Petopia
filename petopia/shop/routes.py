from flask import Blueprint, render_template, session, url_for, redirect, make_response, request, flash
from petopia.shop.models import Product, Category, Cart, Order, OrderItem
from petopia import db

shop = Blueprint('shop', __name__, static_folder='templates/static', template_folder='templates')


@shop.route('/')
def home():
    return render_template('home.html')


@shop.route('/details/<slug>', methods=['POST', 'GET'])
def details(slug):
    product = Product.query.filter_by(slug=slug).first_or_404()
    if request.method == 'POST':
        item = request.form.get('product_id', None)
        if item:
            cart = Cart(session)
            cart.add_or_update(item)
        return render_template('parts/cart_menu.html')
    return render_template('details.html', product=product)


@shop.route('/search')
def search():
    query = request.args.get('query', None)
    page = request.args.get('page', 1)
    per_page = 8
    products =  []

    if query:
        products = Product.query.filter(db.or_(
            Product.name.icontains(query),
            Product.description.icontains(query)
        )).paginate(
            page=int(page),
            per_page=per_page
            )

    return render_template('search.html', products=products, query=query)


@shop.route('/main-shop')
def main_shop():
    categories = Category.query.all()
    category_selected = request.args.get('category', None)
    page = request.args.get('page', 1)
    per_page = 8
    products = Product.query.paginate(page=int(page), per_page=per_page) if not category_selected else Product.query.filter_by(
        category_id=category_selected
        ).paginate(page=int(page), per_page=per_page)

    context = {
        'categories': categories,
        'products': products, 
        'category_selected': category_selected, 
        'category_name': Category.query.filter_by(id=category_selected).first().name if category_selected else None
    }
    return render_template('shop.html', **context)


@shop.route('/cart', methods=['GET', 'POST'])
def cart_page():
    return render_template('cart.html')

@shop.route('/cart-update/<product_id>/<action>')
def cart_update(product_id, action):
    cart = Cart(session)

    if action == 'increment':
        cart.add_or_update(product_id, 1)
    elif action == 'decrement':
        cart.add_or_update(product_id, -1)

    product = Product.query.filter_by(id=int(product_id)).first()
    cart_item = cart.get_item(product_id)

    if cart_item:
        item = {
            'product_id': product.id,
            'product': {
                'name': product.name,
                'price': product.price,
            },
            'slug': product.slug,
            'total_price': product.price * int(cart_item['quantity']),
            'quantity': cart_item['quantity'],
        }

    else:
        item = None

    response = make_response(render_template('parts/cart_item.html', item=item))
    response.headers["HX-Trigger"] = "update-cart-menu"
    return response


@shop.route('/get-cart-count')
def get_cart_count():
    return render_template('parts/cart_menu.html')

@shop.route('/get-total-amount')
def get_total_amount():
    return render_template('parts/total_amount.html')

@shop.route('/checkout', methods=['GET', 'POST'])
def checkout():
    cart = Cart(session)
    if cart.__len__() == 0:
        return redirect(url_for('shop.cart_page'))

    if request.method == 'POST':
        full_name = request.form['full_name']
        email_address = request.form['email_address']
        city = request.form['city']
        postal_code = int(request.form['postal_code'])
        state = request.form['state']
        phone_no = int(request.form['phone_no'])
        nearest_landmark = request.form['nearest_landmark']

        try:
            order = Order(
                full_name=full_name,
                email_address=email_address,
                city=city,
                postal_code=postal_code,
                state=state,
                phone_no=phone_no,
                nearest_landmark=nearest_landmark,
                total_amount=int(cart.get_total_amount())
            )
            db.session.add(order)

            for item in cart:
                order_item = OrderItem(
                    product_id = item['product_id'],
                    quantity = item['quantity'],
                    order_id = order.id
                )
                db.session.add(order_item)

            db.session.commit()

            cart.clear()
            return redirect(url_for('shop.success'))

        except:
            flash('Oops something went wrong...', category='error')
            return redirect(url_for('shop.checkout'))

    return render_template('checkout.html')

@shop.route('/succss')
def success():
    return render_template('success.html')
