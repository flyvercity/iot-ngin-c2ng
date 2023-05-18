import os
from datetime import datetime, timedelta
from pathlib import Path
from argparse import ArgumentParser
from dotenv import load_dotenv

from cryptography import x509
from cryptography.hazmat.primitives import hashes

from cryptography.hazmat.primitives.serialization import (
    Encoding, PrivateFormat, BestAvailableEncryption
)

from service.secman import generate_pk, get_subject

SERVCE_CERTIFICATE_LIFESPAN_DAYS = 365


def gen_ss_cert(service_key, issuer):
    subject = issuer

    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        service_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.utcnow()
    ).not_valid_after(
        datetime.utcnow() + timedelta(days=SERVCE_CERTIFICATE_LIFESPAN_DAYS)
    ).sign(service_key, hashes.SHA256())

    return cert


def main():
    parser = ArgumentParser()

    parser.add_argument(
        '-p', '--private',
        help='PEM file for the private key', default='config/c2ng/private.pem'
    )

    parser.add_argument(
        '-c', '--certificate',
        help='PEM file for root certificate', default='config/c2ng/service.pem'
    )

    args = parser.parse_args()
    service_key = generate_pk()
    issuer = get_subject('root.c2ng')
    service_sscert = gen_ss_cert(service_key, issuer)

    passphrase = os.getenv('C2NG_UAS_CLIENT_SECRET').encode()

    Path(args.private).write_bytes(
        service_key.private_bytes(
            Encoding.PEM,
            PrivateFormat.TraditionalOpenSSL,
            BestAvailableEncryption(passphrase)
        )
    )

    Path(args.certificate).write_bytes(service_sscert.public_bytes(Encoding.PEM))


if __name__ == '__main__':
    load_dotenv()
    main()
