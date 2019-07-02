#!/usr/bin/python

import sys
from OpenSSL import crypto
from os.path import exists, join

CERT_FILE = "selfsigned.crt"
KEY_FILE = "private.key"


def create_self_signed_cert(cert_dir):
    """
    If selfsigned.crt and private.key don't exist in cert_dir, create a new
    self-signed cert and keypair and write them into that directory.
    """

    if not exists(join(cert_dir, CERT_FILE)) or not exists(join(cert_dir, KEY_FILE)):
        # create a key pair
        k = crypto.PKey()
        k.generate_key(crypto.TYPE_RSA, 2048)

        # create a self-signed cert
        cert = crypto.X509()
        cert.get_subject().C = "US"
        cert.get_subject().ST = "NC"
        cert.get_subject().L = "Cary"
        cert.get_subject().O = "Self-Signed Viya Certificate"
        cert.get_subject().OU = "SASViya"
        # cert.get_subject().CN = "sasInstallCA" # USE ONCE DNS IS CREATED
        cert.get_subject().CN = str(sys.argv[1])  # LOAD BALANCER IP ADDRESS
        cert.set_serial_number(1000)
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(10 * 365 * 24 * 60 * 60)
        cert.set_issuer(cert.get_subject())
        cert.set_pubkey(k)
        cert.sign(k, 'sha256')

        open(join(cert_dir, CERT_FILE), "wt").write(
            crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
        open(join(cert_dir, KEY_FILE), "wt").write(
            crypto.dump_privatekey(crypto.FILETYPE_PEM, k))


create_self_signed_cert("/tmp")
