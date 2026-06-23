import stripe
from django.conf import settings
from decimal import Decimal

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    """Сервис для работы со Stripe API"""

    @staticmethod
    def create_product(course):
        """Создание продукта в Stripe"""
        try:
            product = stripe.Product.create(
                name=course.title,
                description=course.description[:500] if course.description else "",
                metadata={
                    'course_id': course.id,
                    'course_title': course.title,
                }
            )
            return product.id
        except stripe.error.StripeError as e:
            print(f"Stripe error creating product: {e}")
            return None

    @staticmethod
    def create_price(amount, product_id, course_title):
        """Создание цены для продукта"""
        try:
            # Конвертируем сумму в копейки/центы
            amount_in_cents = int(Decimal(str(amount)) * 100)

            price = stripe.Price.create(
                product=product_id,
                unit_amount=amount_in_cents,
                currency='rub',
                nickname=f"Курс: {course_title}",
            )
            return price.id
        except stripe.error.StripeError as e:
            print(f"Stripe error creating price: {e}")
            return None

    @staticmethod
    def create_checkout_session(price_id, course_id, user_email, success_url, cancel_url):
        """Создание сессии для оплаты"""
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price': price_id,
                        'quantity': 1,
                    },
                ],
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                customer_email=user_email,
                metadata={
                    'course_id': course_id,
                    'user_email': user_email,
                },
            )
            return checkout_session.id, checkout_session.url
        except stripe.error.StripeError as e:
            print(f"Stripe error creating checkout session: {e}")
            return None, None

    @staticmethod
    def retrieve_checkout_session(session_id):
        """Получение информации о сессии оплаты"""
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            return session
        except stripe.error.StripeError as e:
            print(f"Stripe error retrieving session: {e}")
            return None

    @staticmethod
    def retrieve_payment_intent(payment_intent_id):
        """Получение информации о платеже"""
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            return payment_intent
        except stripe.error.StripeError as e:
            print(f"Stripe error retrieving payment intent: {e}")
            return None