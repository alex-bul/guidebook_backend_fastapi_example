import decimal
import hashlib
from urllib import parse
from urllib.parse import urlparse


def calculate_signature(*args) -> str:
    """Create signature MD5.
    """
    return hashlib.md5(':'.join(str(arg) for arg in args).encode()).hexdigest()


def parse_response(request: str) -> dict:
    """
    :param request: Link.
    :return: Dictionary.
    """
    params = {}
    for item in request.split('&'):
        key, value = item.split('=')
        params[key] = value
    return params


def check_signature_result(
        order_number: int,  # invoice number
        received_sum: decimal,  # cost of goods, RU
        received_signature: hex,  # SignatureValue
        password: str,  # Merchant password
        *addition_params
) -> bool:
    signature = calculate_signature(received_sum, order_number, password, *addition_params)
    if signature.lower() == received_signature.lower():
        return True
    return False


# Формирование URL переадресации пользователя на оплату.

def generate_payment_link(
        merchant_login: str,  # Merchant login
        merchant_password_1: str,  # Merchant password
        cost: decimal,  # Cost of goods, RU
        number: int,  # Invoice number
        description: str,  # Description of the purchase
        is_test=0,
        robokassa_payment_url='https://auth.robokassa.ru/Merchant/Index.aspx',
        **kwargs
) -> str:
    """URL for redirection of the customer to the service.
    """
    signature_addition_params = [f"{key}={val}" for key, val in sorted(list(kwargs.items()))]
    signature = calculate_signature(
        merchant_login,
        cost,
        number,
        merchant_password_1,
        *signature_addition_params
    )

    data = {
        'MerchantLogin': merchant_login,
        'OutSum': cost,
        'InvId': number,
        'Description': description,
        'SignatureValue': signature,
        'IsTest': is_test,
        **kwargs
    }
    return f'{robokassa_payment_url}?{parse.urlencode(data)}'


# Получение уведомления об исполнении операции (ResultURL).

def result_payment(merchant_password_2: str, request: str) -> str:
    """Verification of notification (ResultURL).
    :param request: HTTP parameters.
    """
    param_request = parse_response(request)
    cost = param_request['OutSum']
    number = param_request['InvId']
    signature = param_request['SignatureValue']

    addition_params = []
    for key, val in param_request.items():
        if key.startswith('shp_'):
            addition_params.append(f"{key}={val}")
    addition_params.sort()

    if check_signature_result(number, cost, signature, merchant_password_2, *addition_params):
        return f'OK{param_request["InvId"]}'
    return "bad sign"
