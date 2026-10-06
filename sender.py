import socket
import sys
import signal
from typing import Optional

from DES_cipher import des_encrypt_ecb, des_decrypt_ecb

DEFAULT_PORT = 5000
BUFFER_SIZE = 4096
HEADER_SIZE = 4
ENCODING = "utf-8"


def kirim_pesan(sock: socket.socket, data: bytes) -> None:
    """Mengirim data dengan header panjang 4-byte."""
    panjang = len(data)
    header = panjang.to_bytes(HEADER_SIZE, byteorder="big")
    sock.sendall(header + data)


def terima_pesan(sock: socket.socket) -> Optional[bytes]:
    """Menerima data dengan membaca header panjang terlebih dahulu."""
    header = _recv_exact(sock, HEADER_SIZE)
    if header is None:
        return None

    panjang = int.from_bytes(header, byteorder="big")
    if panjang == 0:
        return b""

    return _recv_exact(sock, panjang)


def _recv_exact(sock: socket.socket, n: int) -> Optional[bytes]:
    """Membaca tepat n byte dari socket."""
    data = bytearray()
    while len(data) < n:
        try:
            chunk = sock.recv(n - len(data))
            if not chunk:
                return None
            data.extend(chunk)
        except ConnectionError:
            return None
    return bytes(data)


def main() -> None:
    """Fungsi utama sender: koneksi, enkripsi pesan, dan komunikasi dua arah."""
    print("=== SENDER (Client DES) ===")

    ip_receiver = input(f"Masukkan IP receiver (default: 127.0.0.1): ").strip()
    if not ip_receiver:
        ip_receiver = "127.0.0.1"

    port_str = input(f"Masukkan port (default: {DEFAULT_PORT}): ").strip()
    try:
        port = int(port_str) if port_str else DEFAULT_PORT
    except ValueError:
        print("Port tidak valid, menggunakan default.")
        port = DEFAULT_PORT

    while True:
        secret_key = input("Masukkan secret key (8 karakter): ").strip()
        if len(secret_key) == 8:
            break
        print(f"Key harus tepat 8 karakter! (Panjang saat ini: {len(secret_key)})")

    key_bytes = secret_key.encode(ENCODING)

    print(f"\nMenghubungi receiver di {ip_receiver}:{port}...")

    client_socket: Optional[socket.socket] = None

    def signal_handler(sig, frame):
        print("\n\nCtrl+C terdeteksi. Menutup koneksi...")
        if client_socket:
            try:
                client_socket.close()
            except Exception:
                pass
        print("Koneksi ditutup.")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((ip_receiver, port))
        print(f"Terhubung ke receiver di {ip_receiver}:{port}")
        print(f"Secret key : \"{secret_key}\"")
        print("\nKetik pesan untuk dikirim ('exit' atau 'quit' untuk keluar).\n")

    except ConnectionRefusedError:
        print(f"Error: Koneksi ditolak. Pastikan receiver sudah aktif di {ip_receiver}:{port}")
        sys.exit(1)
    except socket.timeout:
        print("Error: Koneksi timeout. Periksa IP dan port receiver.")
        sys.exit(1)
    except OSError as e:
        print(f"Error koneksi: {e}")
        sys.exit(1)

    try:
        while True:
            try:
                pesan = input("\n[ANDA] > ")
            except EOFError:
                break

            if pesan.strip().lower() in ("exit", "quit"):
                print("Menutup koneksi...")
                try:
                    kirim_pesan(client_socket, b"__EXIT__")
                except Exception:
                    pass
                break

            if not pesan.strip():
                print("(Pesan kosong, tidak dikirim)")
                continue

            plaintext_bytes = pesan.encode(ENCODING)
            ciphertext = des_encrypt_ecb(plaintext_bytes, key_bytes)

            try:
                kirim_pesan(client_socket, ciphertext)
            except (BrokenPipeError, ConnectionError) as e:
                print(f"Koneksi terputus saat mengirim: {e}")
                break

            print(f"   Plaintext  : \"{pesan}\"")
            print(f"   Ciphertext : {ciphertext.hex().upper()}")
            print(f"   Ukuran     : {len(plaintext_bytes)} byte -> {len(ciphertext)} byte")

            print("\n   Menunggu balasan dari receiver...")
            try:
                balasan_ct = terima_pesan(client_socket)
            except Exception as e:
                print(f"Error menerima balasan: {e}")
                break

            if balasan_ct is None:
                print("Receiver menutup koneksi.")
                break

            if balasan_ct == b"__EXIT__":
                print("Receiver mengakhiri sesi.")
                break

            try:
                balasan_pt = des_decrypt_ecb(balasan_ct, key_bytes)
                balasan_text = balasan_pt.decode(ENCODING)

                print(f"   Ciphertext diterima : {balasan_ct.hex().upper()}")
                print(f"   Plaintext (balasan) : \"{balasan_text}\"")
                print(f"   [RECEIVER] > {balasan_text}")
            except Exception as e:
                print(f"Error dekripsi balasan: {e}")
                print(f"Ciphertext raw: {balasan_ct.hex().upper()}")

    except (ConnectionError, BrokenPipeError):
        print("\nKoneksi terputus tiba-tiba.")

    finally:
        if client_socket:
            try:
                client_socket.close()
            except Exception:
                pass
        print("Sesi sender berakhir.")


if __name__ == "__main__":
    main()
