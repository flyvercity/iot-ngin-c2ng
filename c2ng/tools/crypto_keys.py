# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

'''A CLI tool for pre-configuration of root security credentials.'''
import os
from datetime import datetime, timedelta
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey

from cryptography.hazmat.primitives.serialization import (
    Encoding, PrivateFormat, BestAvailableEncryption
)

from c2ng.service.backend.secman import generate_pk, get_x509_subject


SERVICE_CERTIFICATE_LIFESPAN_DAYS = 365
'''A lifetime of the root certificate.'''


def gen_ss_cert(service_key: RSAPrivateKey, issuer: x509.Name):
    '''Generates a self-signed certificate.

    Args:
        service_key: generated private key of the service itself
        issuer: own X.509 name to be used both as the issuer and the subject

    Returns:
        X509 certificate
    '''

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
        datetime.utcnow() + timedelta(days=SERVICE_CERTIFICATE_LIFESPAN_DAYS)
    ).sign(service_key, hashes.SHA256())

    return cert


def add_arg_subparsers(sp):
    cryptokeys = sp.add_parser('genapi', help='Generate crypto keys')

    cryptokeys.add_argument(
        '-p', '--private',
        help='PEM file for the private key',
        default='docker/core/config/c2ng/private.pem'
    )

    cryptokeys.add_argument(
        '-c', '--certificate',
        help='PEM file for root certificate',
        default='docker/core/config/c2ng/service.pem'
    )


async def run(args):
    service_key = generate_pk()
    issuer = get_x509_subject('root.c2ng')
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
