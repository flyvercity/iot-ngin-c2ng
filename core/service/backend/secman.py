# SPDX-License-Identifier: MIT
# Copyright 2023 Flyvercity

'''This module defines Security Credentials Manager.'''

import os
from datetime import datetime, timedelta
from pathlib import Path
import logging as lg
from uuid import uuid4

from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes

from cryptography.hazmat.primitives.serialization import (
    load_pem_private_key,
    Encoding,
    PrivateFormat,
    BestAvailableEncryption
)


def generate_pk():
    '''Generate key-pair with standard parameters.

    Returns:
        A newly generated RSA key pair.
    '''

    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


def get_x509_subject(name: str):
    '''Construct X.509 Subject.

    Args:
        name: What to use as 'common name'.

    Returns:
        A constructed X509 issuer/subject name.
    '''

    subject = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, 'IL'),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, 'HaSharon'),
        x509.NameAttribute(NameOID.LOCALITY_NAME, 'Netanya'),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, 'Flyvercity LTD'),
        x509.NameAttribute(NameOID.COMMON_NAME, f'{name}.flyvecity.com')
    ])

    return subject


class SecCredentials:
    '''Typed Client Security Credentials'''

    def __init__(
            self, 
            kid: str,
            cert: x509.Certificate,
            key: rsa.RSAPrivateKey,
            client_secret: str
    ):
        '''Constructor

        Args:
            kid: key unique identifier
            cert: X509 client certificate
            key: client session key
            client_secret: static client secret used to encrypt session keys
        '''

        self._kid = kid
        self._cert = cert
        self._key = key
        self._client_secret = client_secret

    def kid(self):
        '''Get a key identifier.

        Returns:
            A key identifier as a string.
        '''
        return self._kid

    def cert(self):
        '''Get a certificate string.

        Returns:
            A certificate with a public key as a PEM string.
        '''
        return self._cert.public_bytes(Encoding.PEM).decode()

    def key(self):
        '''Get a private key.

        Returns:
            An encrypted session private key as a PEM string.
        '''
        return self._key.private_bytes(
            Encoding.PEM,
            PrivateFormat.TraditionalOpenSSL,
            BestAvailableEncryption(self._client_secret.encode())
        ).decode()


class SecMan:
    '''Security credentials manager '''

    def __init__(self, config):
        '''Creates an instance of the manager and loads root credentials

        Args:
            config: `security` section of the configuration file
        '''

        self._config = config
        self._root_cert = x509.load_pem_x509_certificate(Path(config['certificate']).read_bytes())
        lg.info(f'Certificate loaded: {self._root_cert.serial_number}')
        passphrase = os.getenv('C2NG_UAS_CLIENT_SECRET').encode()

        self._private_key = load_pem_private_key(
            Path(config['private']).read_bytes(),
            passphrase
        )

        lg.info('Private key loaded')

    def gen_client_credentials(self, client_id):
        '''Generates session security credentials.

        Args:
            client_id: UA or ADX user logical identifier.

        Returns:
            `SecCredentials` object.

        Raises:
            RuntimeError: when there no configured secret to for a stored key
        '''
        # TODO: find out how to use individual key for each user
        oauth_client_id = os.getenv('C2NG_UAS_CLIENT_SECRET')

        if not oauth_client_id:
            raise RuntimeError('Not UAS OAuth client secret configured')

        kid = str(uuid4())
        client_key = generate_pk()
        subject = get_x509_subject(f'{client_id}.c2ng')
        ttl = self._config['default-ttl']

        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            self._root_cert.issuer
        ).public_key(
            client_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(seconds=ttl)
        ).sign(self._private_key, hashes.SHA256())

        return SecCredentials(kid, cert, client_key, oauth_client_id)
