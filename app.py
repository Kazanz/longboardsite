import stripe
from flask import Flask, render_template, request, jsonify, redirect, url_for
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker


from local import SECRET_KEY, PUBLISHABLE_KEY


app = Flask(__name__, template_folder="templates", static_folder="static")
stripe_keys = {
    'secret_key': SECRET_KEY,
    'publishable_key': PUBLISHABLE_KEY
}
stripe.api_key = stripe_keys['secret_key']

Base = declarative_base()


class Affiliate(Base):
    __tablename__ = 'affiliates'
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False, primary_key=True)
    address = Column(String(500), nullable=False)
    code = Column(String(8), nullable=False, unique=True)
    count = Column(Integer, default=0)


engine = create_engine('sqlite:///vitesse.db')
try:
    Base.metadata.create_all(engine)
except:
    pass
DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
def index():
    return render_template('index.html', key=stripe_keys['publishable_key'])


@app.route('/thank-you/<string:order_number>')
def thank_you(order_number):
    return render_template('thank_you.html', order_number=order_number)


@app.route('/charge', methods=['POST'])
def charge():
    amount = 62900
    shipping = {
        'address': {
            'line1': request.form['shipping_address_line1'],
            'city': request.form['shipping_address_city'],
            'state': request.form['shipping_address_state'],
            'postal_code': request.form['shipping_address_zip'],
            'country': request.form['shipping_address_country'],
        },
        'name': request.form['shipping_name'],
    }
    customer = stripe.Customer.create(
        email=request.form['card[name]'],
        card=request.form['id'],
        shipping=shipping,
    )
    charge = stripe.Charge.create(
        customer=customer.id,
        amount=amount,
        currency='usd',
        description='Qty 1: Vitesse Electric Longboard'
    )

    code = request.form.get('code')
    if code:
        a = session.query(Affiliate).filter_by(code=code).first()
        if a:
            a.count += 1
            session.add(a)
            session.commit()

    return jsonify(order_number=charge.id)


@app.route('/affiliates')
def affiliates():
    affiliates = session.query(Affiliate).order_by('count desc').order_by('name').all()
    return render_template('affiliate.html', affiliates=affiliates)


@app.route('/affiliates/create', methods=['POST'])
def affiliate_make():
    if request.form.get('password') == "JesusIsLord":
        data = {field: request.form[field]
                for field in ('name', 'email', 'address', 'code')}
        a = Affiliate(**data)
        session.add(a)
        try:
            session.commit()
        except Exception as e:
            session.rollback()
            return str(e)
    return redirect(url_for('affiliates'))
