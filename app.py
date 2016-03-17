import os

import stripe
from flask import Flask, render_template, request, jsonify

from local import SECRET_KEY, PUBLISHABLE_KEY


app = Flask(__name__, template_folder="templates", static_folder="static")
stripe_keys = {
    'secret_key': SECRET_KEY,
    'publishable_key': PUBLISHABLE_KEY 
}
stripe.api_key = stripe_keys['secret_key']


@app.route('/')
def index():
    return render_template('index.html', key=stripe_keys['publishable_key'])


@app.route('/thank-you/<string:order_number>')
def thank_you(order_number):
    return render_template('thank_you.html', order_number=order_number)


@app.route('/charge', methods=['POST'])
def charge():
    amount = 69900
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
    return jsonify(order_number=charge.id)
