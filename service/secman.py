from datetime import datetime, timedelta
from pathlib import Path
import logging as lg

from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes


def generate_pk():
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


def get_subject(name):
    subject = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, 'IL'),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, 'HaSharon'),
        x509.NameAttribute(NameOID.LOCALITY_NAME, 'Netanya'),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, 'Flyvercity LTD'),
        x509.NameAttribute(NameOID.COMMON_NAME, f'{name}.flyvecity.com')
    ])

    return subject


class SecMan:
    '''Security credentials manager '''

    def __init__(self, config):
        '''Creates an instance of the manager'''
        self._config = config
        cert_path = Path(config['certificate'])
        self._cert = x509.load_pem_x509_certificate(cert_path.read_bytes())
        lg.info(f'Certificate loaded: {self._cert.serial_number}')

    def generate_keypair():
        return rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )

    def gen_client_cert(issuer, service_key, client_id, client_key):
        subject = get_subject(f'{client_id}.c2ng')

        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            client_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            # Our certificate will be valid for 10 days
            datetime.utcnow() + timedelta(days=1)
        ).sign(service_key, hashes.SHA256())

        return cert


    def validate_client_cert(service_cert, client_cert):
        client_cert.verify_directly_issued_by(service_cert)

