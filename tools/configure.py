from datetime import datetime, timedelta
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import Encoding

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
        # Our certificate will be valid for 10 days
        datetime.utcnow() + timedelta(days=SERVCE_CERTIFICATE_LIFESPAN_DAYS)
    ).sign(service_key, hashes.SHA256())

    return cert


def main():
    service_key = generate_pk()
    issuer = get_subject('root.c2ng')
    service_sscert = gen_ss_cert(service_key, issuer)
    Path('config/c2ng/service.pem').write_bytes(service_sscert.public_bytes(Encoding.PEM))


if __name__ == '__main__':
    main()
