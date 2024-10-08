from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.utils import timezone
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Paies
import hashlib
import json
import binascii

MerchantID = settings.ENCRYPTION_KEY['MERCHANT_ID']
HASHKEY = settings.ENCRYPTION_KEY['HASH_KEY']
HASHIV = settings.ENCRYPTION_KEY['HASH_IV']
Version = settings.ENCRYPTION_KEY['VERSION']
ReturnUrl = settings.ENCRYPTION_KEY['RETURN_URL']
NotifyUrl = settings.ENCRYPTION_KEY['NOTIFY_URL']
PayGateWay = settings.ENCRYPTION_KEY['PAY_GATEWAY']
RespondType = settings.ENCRYPTION_KEY['RESPOND_TYPE']

def index(request):
    return render(request, 'paies/index.html', {'title': 'Express'})

@csrf_exempt
def create_order(request):
    if request.method == 'POST':
        member = request.user
        timestamp = int(timezone.now().timestamp())
        order = {
            'MerchantID': MerchantID,
            # 'RespondType': 'String',
            'RespondType': 'JSON',
            'TimeStamp': timestamp,
            'Version': 2.0,
            'Amt': int(100),
            'MerchantOrderNo': timestamp,
            'ItemDesc': 'Premium會員',
            'ReturnURL': ReturnUrl,
            'NotifyURL': NotifyUrl,
            'CREDIT': 1,
        }

        save_order = Paies(
            member = member,
            order = order['MerchantOrderNo'],
            amount = order['Amt'],
            merchant_id = order['MerchantID'],
            version = order['Version'],
            item_desc = order['ItemDesc'],
            return_url = order['ReturnURL'],
            notify_url = order['NotifyURL']
        )
        save_order.save()
        return redirect('paies:check_order', timestamp)


    return HttpResponse('Method Not Allowed', status=405)

def gen_data_chain(order):
    return f"MerchantID={order['MerchantID']}&TimeStamp={order['TimeStamp']}&Version={order['Version']}&RespondType={order['RespondType']}&MerchantOrderNo={order['MerchantOrderNo']}&Amt={int(order["Amt"])}&NotifyURL={order['NotifyURL']}&ReturnURL={order['ReturnURL']}&ItemDesc={order['ItemDesc']}"


def aes_encrypt(data):
    key_bytes = HASHKEY.encode('utf-8')
    iv_bytes = HASHIV.encode('utf-8')

    cipher = Cipher(algorithms.AES(key_bytes), modes.CBC(iv_bytes), backend=default_backend())

    encryptor = cipher.encryptor()

    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(data.encode('utf-8')) + padder.finalize()

    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    return ciphertext.hex()

def create_sha_encrypt(edata1):
    hash_string = f"HashKey={HASHKEY}&{edata1}&HashIV={HASHIV}"
    print(f"====hash_string==== {hash_string}")

    sha256_hash = hashlib.sha256(hash_string.encode()).hexdigest()

    return sha256_hash.upper()

@csrf_exempt
def check_order(request, TimeStamp):
    str_timestamp = TimeStamp

    order = get_object_or_404(Paies, order=str_timestamp)

    data_chain = gen_data_chain({
        'MerchantID': MerchantID,
        'RespondType': 'JSON',
        'TimeStamp': order.order,
        'Version': '2.0',
        'Amt': order.amount,
        'MerchantOrderNo': order.order,
        'ItemDesc': 'Premium會員',
        'ReturnURL': ReturnUrl,
        'NotifyURL': NotifyUrl,
        'CREDIT': 1,
    })
    print(f"====data_chain==== {data_chain}")
    
    encrypted_data = aes_encrypt(data_chain)
    print(f"====encrypted_data==== {encrypted_data}")

    sha_encrypt = create_sha_encrypt(encrypted_data)

    print(f"====sha_encrypt==== {sha_encrypt}")

    return render(request, 'paies/check.html', {
        'MerchantID': MerchantID,
        'TradeInfo': encrypted_data,
        'TradeSha': sha_encrypt,
        'Version': Version,
        'MerchantOrderNo': order.order,
        'ItemDesc': order.item_desc,
    })

@csrf_exempt
def newebpay_return(request):
    print(f'=====POST: {request.POST}=====')
    if request.method == 'POST':
        enc_data = request.POST.get('TradeInfo')
        print(f'=====enc_data: {enc_data}=====')
        decrypt = decrypt_aes_cbc(enc_data, HASHKEY, HASHIV)
        print(f'=====decrypt: {decrypt}=====')
        decrypt_dict = json.loads(decrypt)
        print(f'=====decrypt_dict: {decrypt_dict}=====')

        merchant_order = decrypt_dict["Result"]["MerchantOrderNo"]

        try:
            update_order = Paies.objects.get(order=merchant_order)
            update_order.amount = decrypt_dict["Result"]["Amt"]
            update_order.status = decrypt_dict["Status"]
            update_order.paid_at = decrypt_dict["Result"]["PayTime"]
            update_order.save()
            
            member = update_order.member
            member.member_status = "1"  

            member.save()

            return render(request, 'paies/success.html')
        except Paies.DoesNotExist:
            return HttpResponse("訂單不存在", status=404)
        
    else:
        return HttpResponse("Method Not Allowed", status=405)

# @csrf_exempt
# def newebpay_notify(request):
#     if request.method == 'POST':
#         return HttpResponse('Notify')
#     else:
#         return HttpResponse("Method Not Allowed", status=405)


def checkout_success(request):
    return render(request, 'paies/success.html', {'title': 'Checkout Success'})

def decrypt_aes_cbc(encrypted_data, key, iv):
    try:
        key_bytes = key.encode('utf-8')
        print(f"=====key_bytes==== {key_bytes}")
        print(f"Key length: {len(key_bytes)}")  # 應該是 32

        iv_bytes = iv.encode('utf-8')
        print(f"=====iv_bytes==== {iv_bytes}")
        print(f"IV length: {len(iv_bytes)}")

        encrypted_bytes = binascii.unhexlify(encrypted_data)
        # encrypted_bytes = bytes.fromhex(encrypted_data)
        print(f"=====encrypted_bytes==== {encrypted_bytes}")
        # print(f"=====encrypted_data==== {encrypted_data}")

        cipher = Cipher(algorithms.AES(key_bytes), modes.CBC(iv_bytes), backend=default_backend())
        print(f"=====cipher==== {cipher}")
        
        decryptor = cipher.decryptor()
        print(f"=====decryptor==== {decryptor}")

        decrypted_padded_data = decryptor.update(encrypted_bytes) + decryptor.finalize()
        print(f"=====decrypted_padded_data==== {decrypted_padded_data}")

        plain = strip_padding(decrypted_padded_data)
        # unpadder = padding.PKCS7(128).unpadder()
        # print(f"=====unpadder==== {unpadder}")

        # decrypted_data = unpadder.update(decrypted_padded_data) + unpadder.finalize()
        # print(f"=====decrypted_data==== {decrypted_data}")

        return plain
        # return decrypted_data.decode('utf-8')
    except Exception as e:
        print(f"解密失敗：{e}")
        return None
    
# 移除填充字節
def strip_padding(data):
    slast = data[-1]
    return data[:-slast].decode("utf-8")