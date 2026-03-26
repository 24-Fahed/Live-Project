import ipaddress
from datetime import datetime, timedelta
from pathlib import Path

from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from app.subsystems.hls.config import CERT_DIR, CERT_FILE, KEY_FILE, CERT_VALIDITY_DAYS, CERT_COMMON_NAME, CERT_SAN_NAMES


def ensure_certs() -> tuple[str, str]:
    """确保证书存在，不存在则自动生成。

    Returns:
        (cert_file_path, key_file_path)
    """
    cert_path = Path(CERT_FILE)
    key_path = Path(KEY_FILE)

    if cert_path.exists() and key_path.exists():
        return str(cert_path), str(key_path)

    # 创建证书目录
    Path(CERT_DIR).mkdir(parents=True, exist_ok=True)

    # 生成私钥
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # 构建主题名称
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "CN"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Beijing"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Beijing"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Live Debate Gateway"),
        x509.NameAttribute(NameOID.COMMON_NAME, CERT_COMMON_NAME),
    ])

    # 构建 SAN（Subject Alternative Name）
    san_list = [x509.DNSName(name) for name in CERT_SAN_NAMES]
    san_list.append(x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")))

    # 构建证书
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.utcnow()
    ).not_valid_after(
        datetime.utcnow() + timedelta(days=CERT_VALIDITY_DAYS)
    ).add_extension(
        x509.SubjectAlternativeName(san_list),
        critical=False,
    ).sign(private_key, hashes.SHA256())

    # 保存私钥
    with open(key_path, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        ))

    # 保存证书
    with open(cert_path, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    return str(cert_path), str(key_path)
