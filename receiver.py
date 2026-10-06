import socket
import sys
import signal
from typing import Optional

from DES_cipher import des_encrypt_ecb, des_decrypt_ecb

DEFAULT_PORT = 5000
BUFFER_SIZE = 4096
HEADER_SIZE = 4
ENCODING = "utf-8"

# Mengirim data dengan header panjang 4-byte 
def kirim_pesan(sock: socket.socket, data: bytes) -> None:
    panjang = len(data)
    header = panjang.to_bytes(HEADER_SIZE, byteorder="big")
    sock.sendall(header + data)


# Menerima data dengan membaca header panjang terlebih dahulu
def terima_pesan(sock: socket.socket) -> Optional[bytes]:
    header = _recv_exact(sock, HEADER_SIZE)
    if header is None:
        return None

    panjang = int.from_bytes(header, byteorder="big")
    if panjang == 0:
        return b""

    return _recv_exact(sock, panjang)


# Membaca tepat n byte dari socket
def _recv_exact(sock: socket.socket, n: int) -> Optional[bytes]:
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
    # Fungsi utama receiver: listen socket, dekripsi pesan, dan kirim balasan.
    print("Receiver")

    port_str = input(f"Masukkan port untuk listen (default: {DEFAULT_PORT}): ").strip()
    try:
        port = int(port_str) if port_str else DEFAULT_PORT
    except ValueError:
        print("Port tidak valid, menggunakan default.")
        port = DEFAULT_PORT

    while True:
        secret_key = input("Masukkan secret key (8 karakter dan harus sama dengan sender): ").strip()
        if len(secret_key) == 8:
            break
        print(f"Key harus tepat 8 karakter! (Panjang saat ini: {len(secret_key)})")

    key_bytes = secret_key.encode(ENCODING)

    server_socket: Optional[socket.socket] = None
    client_socket: Optional[socket.socket] = None

    def signal_handler(sig, frame):
        print("\nMenutup server...")
        if client_socket:
            try:
                client_socket.close()
            except Exception:
                pass
        if server_socket:
            try:
                server_socket.close()
            except Exception:
                pass
        print("Server ditutup.")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(("0.0.0.0", port))
        server_socket.listen(1)

        print(f"\nServer berjalan di port {port}")
        print(f"Secret key : \"{secret_key}\"")
        print("Menunggu koneksi dari sender...")

    except OSError as e:
        if "Address already in use" in str(e) or "10048" in str(e):
            print(f"Error: Port {port} sudah digunakan oleh proses lain.")
        else:
            print(f"Error membuat server: {e}")
        sys.exit(1)

    try:
        client_socket, alamat_sender = server_socket.accept()
        print(f"Sender terhubung dari {alamat_sender[0]}:{alamat_sender[1]}")
        print("\nMenerima pesan dan dapat membalas ('exit' atau 'quit' untuk keluar).\n")

    except OSError as e:
        print(f"Error saat menerima koneksi: {e}")
        server_socket.close()
        sys.exit(1)

    try:
        while True:
            print("\n   Menunggu pesan dari sender...")
            try:
                pesan_ct = terima_pesan(client_socket)
            except Exception as e:
                print(f"Error menerima pesan: {e}")
                break

            if pesan_ct is None:
                print("Sender menutup koneksi.")
                break

            if pesan_ct == b"__EXIT__":
                print("Sender mengakhiri sesi.")
                break

            try:
                pesan_pt = des_decrypt_ecb(pesan_ct, key_bytes)
                pesan_text = pesan_pt.decode(ENCODING)

                print(f"   Ciphertext diterima : {pesan_ct.hex().upper()}")
                print(f"   Plaintext (dekripsi): \"{pesan_text}\"")
                print(f"   Ukuran              : {len(pesan_ct)} byte -> {len(pesan_pt)} byte")
                print(f"\n   [SENDER] > {pesan_text}")
            except Exception as e:
                print(f"Error dekripsi pesan: {e}")
                print(f"Ciphertext raw: {pesan_ct.hex().upper()}")
                print("(Pastikan secret key sama persis dengan sender)")
                continue

            try:
                balasan = input("\n[ANDA] > ")
            except EOFError:
                break

            if balasan.strip().lower() in ("exit", "quit"):
                print("Menutup koneksi...")
                try:
                    kirim_pesan(client_socket, b"__EXIT__")
                except Exception:
                    pass
                break

            if not balasan.strip():
                balasan = "(tidak ada balasan)"

            balasan_bytes = balasan.encode(ENCODING)
            balasan_ct = des_encrypt_ecb(balasan_bytes, key_bytes)

            try:
                kirim_pesan(client_socket, balasan_ct)
            except (BrokenPipeError, ConnectionError) as e:
                print(f"Koneksi terputus saat mengirim: {e}")
                break

            print(f"   Plaintext  : \"{balasan}\"")
            print(f"   Ciphertext : {balasan_ct.hex().upper()}")

    except (ConnectionError, BrokenPipeError):
        print("\nKoneksi terputus tiba-tiba.")

    finally:
        if client_socket:
            try:
                client_socket.close()
            except Exception:
                pass
        if server_socket:
            try:
                server_socket.close()
            except Exception:
                pass
        print("Sesi receiver berakhir.")


if __name__ == "__main__":
    main()
