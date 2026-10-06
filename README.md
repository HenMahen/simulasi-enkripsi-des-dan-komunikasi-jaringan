# Simulasi Komunikasi Terenkripsi DES

Tugas Individu - Mata Kuliah Keamanan Informasi
Nama: [Nama Mahasiswa]
NIM : [NIM Mahasiswa]

---

## Deskripsi

Project ini mengimplementasikan simulasi komunikasi dua arah (sender dan receiver) menggunakan algoritma enkripsi **DES (Data Encryption Standard)** secara manual dari nol, tanpa memanfaatkan library kriptografi eksternal.

Komunikasi data dilakukan melalui protokol **TCP socket** dengan model **pre-shared key**, di mana kunci simetris sepanjang 8 karakter telah disepakati oleh pengirim dan penerima sebelum sesi komunikasi berlangsung.

---

## Struktur Folder

```
tugas-01/
├── DES_cipher.py     # Implementasi algoritma DES dan fungsi pengujian
├── sender.py         # Program pengirim (client)
├── receiver.py       # Program penerima (server)
└── README.md         # Dokumentasi project
```

### Fungsi File

| File              | Fungsi                                                                                                                                                                |
| ----------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `DES_cipher.py` | Berisi implementasi tabel permutasi (IP, FP, E, P, PC1, PC2), S-Box, key schedule 16 ronde, fungsi Feistel, enkripsi/dekripsi 1 blok, padding PKCS#7, serta mode ECB. |
| `sender.py`     | Program client TCP yang meminta input pesan, mengenkripsinya dengan DES, mengirimkan ciphertext, dan menerima balasan terenkripsi.                                    |
| `receiver.py`   | Program server TCP yang mendengarkan koneksi, menerima ciphertext, mendekripsinya ke plaintext, dan mengirimkan balasan terenkripsi.                                  |
| `README.md`     | Petunjuk penggunaan, arsitektur sistem, dan panduan pengujian.                                                                                                        |

---

## Cara Kerja DES

```
Plaintext (64 bit)
        |
        v
+-------------------+
| Initial Perm (IP) |
+---------+---------+
          |
     +----+----+
     |         |
    L0        R0     (masing-masing 32 bit)
     |         |
     |    +----+---------------------+
     |    |   RONDE FEISTEL (x16)    |
     |    |                          |
     |    |  Ekspansi E (32 -> 48)   |
     |    |  XOR dengan Subkey (48)  |
     |    |  Substitusi S-Box (8)    |
     |    |  Permutasi P (32)        |
     |    +----+---------------------+
     |         |
    XOR <------+
     |         |
   L1=R0    R1=L0 XOR f(R0, K1)
     |         |
     |    ... ulangi 16 ronde ...
     |         |
     +----+----+
          |
      R16 + L16  (dibalik)
          |
+---------+---------+
| Final Perm (FP)   |
+---------+---------+
          |
          v
Ciphertext (64 bit)
```

### Alur Utama

1. **Initial Permutation (IP)**: Mengubah urutan 64 bit input data.
2. **16 Ronde Feistel**: Melakukan transformasi substitusi-permutasi pada blok kanan (R) yang dikombinasikan dengan subkey tiap ronde, lalu di-XOR ke blok kiri (L).
3. **Key Schedule**: Menghasilkan 16 subkey 48-bit dari kunci awal 64-bit melalui permutasi PC-1, rotasi bit, dan permutasi PC-2.
4. **Final Permutation (FP)**: Invers dari IP untuk menghasilkan ciphertext final.
5. **PKCS#7 Padding**: Memastikan panjang pesan kelipatan 8 byte.

---

## Cara Kerja Komunikasi Socket

```
  SENDER (Client)                              RECEIVER (Server)
+-----------------+                          +-------------------+
|                 |       Koneksi TCP        |                   |
| connect()       |------------------------->| bind() & listen() |
|                 |                          | accept()          |
|                 |                          |                   |
| Input plaintext |                          |                   |
| DES encrypt     |                          |                   |
| kirim pesan     |--- [Header 4B + Data] -->| terima pesan      |
|                 |                          | DES decrypt       |
|                 |                          | Tampilkan pesan   |
|                 |                          |                   |
|                 |                          | Input balasan     |
|                 |                          | DES encrypt       |
| terima balasan  |<-- [Header 4B + Data] ---| kirim balasan     |
| DES decrypt     |                          |                   |
| Tampilkan pesan |                          |                   |
+-----------------+                          +-------------------+
```

Setiap paket data diawali dengan **length prefix** sebesar 4 byte (big-endian unsigned integer) yang merepresentasikan panjang ciphertext. Hal ini mencegah terjadinya *message boundary fragmentation* pada stream TCP.

---

## Petunjuk Menjalankan Program

### 1. Uji Modul DES (Standalone)

Jalankan perintah berikut:

```bash
python DES_cipher.py
```

Pilihan menu yang tersedia:

- `1`: Menjalankan suite pengujian (Test vector resmi NIST FIPS 46-3, pesan pendek, pesan panjang multi-blok, dan pesan batas 8 byte).
- `2`: Mode interaktif untuk melakukan enkripsi atau dekripsi secara manual.
- `3`: Keluar.

### 2. Menjalankan Receiver (Server)

Buka terminal pertama dan jalankan:

```bash
python receiver.py
```

- Masukkan port yang diinginkan (tekan Enter untuk port default `5000`).
- Masukkan kunci rahasia sepanjang tepat 8 karakter (misalnya: `Kunci123`).

### 3. Menjalankan Sender (Client)

Buka terminal kedua dan jalankan:

```bash
python sender.py
```

- Masukkan alamat IP Receiver (tekan Enter untuk `127.0.0.1` jika pada komputer yang sama).
- Masukkan nomor port (harus sama dengan Receiver).
- Masukkan kunci rahasia yang sama persis (`Kunci123`).

Setelah terhubung, masukkan pesan pada terminal sender dan tekan Enter. Receiver akan menampilkan ciphertext yang diterima beserta plaintext hasil dekripsi, lalu meminta input balasan.

Untuk mengakhiri sesi, ketik `exit` atau `quit` pada salah satu terminal, atau gunakan kombinasi tombol `Ctrl+C`.

---

## Skenario Pengujian

### Skenario A: Komunikasi Antar Dua Komputer Fisik (LAN / Wi-Fi)

1. Hubungkan kedua komputer pada jaringan Wi-Fi atau switch LAN yang sama.
2. Cek alamat IP lokal komputer Receiver:
   - Windows: `ipconfig` (lihat bagian IPv4 Address, contoh `192.168.1.15`).
   - Linux/macOS: `ip addr` atau `ifconfig`.
3. Pada komputer Receiver, jalankan `python receiver.py`.
4. Pada komputer Sender, jalankan `python sender.py` dan masukkan IP Receiver tersebut.
5. Pastikan firewall tidak memblokir port yang digunakan (port `5000`).

### Skenario B: Komunikasi Antar Dua Virtual Machine (VM)

1. Konfigurasikan network adapter kedua VM pada VirtualBox/VMware ke mode **Bridged Adapter** atau **Internal Network**.
2. Pastikan kedua VM memperoleh alamat IP yang berada dalam satu subnet dan dapat saling melakukan ping.
3. Jalankan `receiver.py` pada VM pertama dan `sender.py` pada VM kedua.

### Skenario C: Komunikasi Satu Komputer (Localhost)

1. Buka dua jendela terminal terpisah di komputer lokal.
2. Jendela 1: Jalankan `python receiver.py` (gunakan port 5000).
3. Jendela 2: Jalankan `python sender.py` (gunakan IP `127.0.0.1` dan port 5000).

---

## Verifikasi Menggunakan Wireshark

Untuk membuktikan bahwa data yang mengalir di jaringan adalah ciphertext dan bukan plaintext:

1. Buka aplikasi **Wireshark**.
2. Pilih interface jaringan yang aktif:
   - Jaringan LAN/Wi-Fi: pilih interface `Wi-Fi` atau `Ethernet`.
   - Localhost (Windows): pilih adapter `Npcap Loopback Adapter`.
3. Mulai proses capture paket.
4. Terapkan display filter berikut pada Wireshark:
   ```
   tcp.port == 5000
   ```
5. Kirim pesan dari `sender.py` ke `receiver.py`.
6. Pilih salah satu paket TCP bertipe `PSH, ACK` yang membawa payload data.
7. Periksa bagian **Packet Bytes** di panel bawah Wireshark:
   - Karakter yang terlihat pada bagian payload berupa karakter acak biner (ciphertext).
   - Plaintext pesan asli tidak ditemukan pada lalu lintas jaringan.
8. Klik kanan pada paket, lalu pilih **Follow** -> **TCP Stream** untuk mengamati bahwa seluruh aliran data yang ditransmisikan terenkripsi.

---

## Contoh Output Program

### Output Pengujian DES (`DES_cipher.py`)

```
------------------------------------------------------------
TEST VALIDASI IMPLEMENTASI DES
------------------------------------------------------------

[Test 1: Test Vector NIST]
Key         : 133457799BBCDFF1
Plaintext   : 0123456789ABCDEF
Ciphertext  : 85E813540F0AB405
Expected    : 85E813540F0AB405
Hasil       : PASS
Dekripsi    : PASS

[Test 2: Pesan Pendek ('Hello')]
Key         : MyKey123
Plaintext   : 'Hello'
Ciphertext  : ECE18093A04C0D9C
Decrypted   : 'Hello'
Hasil       : PASS

[Test 3: Pesan Panjang (Multi-Blok)]
Key         : MyKey123
Plaintext   : 'Keamanan Informasi adalah mata kuliah yang sangat penting di era digital!'
Ukuran      : 73 byte -> 80 byte ciphertext
Ciphertext  : 314AD0B280E7BB17D38F0BE2E982961CCA147363CE5A9A5C155F42E202063DE495154E9D6A64CA40E164EAAE1C3D6C74536C8CB91AC2D91CB3D0CF7AFFDC7E2C4EB98B6834B7AD068B176D30375AE6BA
Decrypted   : 'Keamanan Informasi adalah mata kuliah yang sangat penting di era digital!'
Hasil       : PASS

[Test 4: Pesan Tepat 8 Byte ('ABCDEFGH')]
Plaintext   : 'ABCDEFGH' (8 byte)
Ciphertext  : 48D15C6FE633C8DFC8845CD349E7423B (16 byte)
Decrypted   : 'ABCDEFGH'
Hasil       : PASS

------------------------------------------------------------
STATUS AKHIR: SEMUA TEST LULUS (PASS)
------------------------------------------------------------
```

### Output Sender (`sender.py`)

```
=== SENDER (Client DES) ===
Masukkan IP receiver (default: 127.0.0.1): 127.0.0.1
Masukkan port (default: 5000): 5000
Masukkan secret key (8 karakter): MyKey123

Menghubungi receiver di 127.0.0.1:5000...
Terhubung ke receiver di 127.0.0.1:5000
Secret key : "MyKey123"

Ketik pesan untuk dikirim ('exit' atau 'quit' untuk keluar).

------------------------------------------------------------

[ANDA] > Halo, ini pesan rahasia!
   Plaintext  : "Halo, ini pesan rahasia!"
   Ciphertext : 72B04E38A3A4D9F8E1293B88...
   Ukuran     : 24 byte -> 32 byte

   Menunggu balasan dari receiver...
   Ciphertext diterima : F4A92B1C...
   Plaintext (balasan) : "Pesan diterima dengan baik."
   [RECEIVER] > Pesan diterima dengan baik.
```

### Output Receiver (`receiver.py`)

```
=== RECEIVER (Server DES) ===
Masukkan port untuk listen (default: 5000): 5000
Masukkan secret key (8 karakter, sama dengan sender): MyKey123

Server berjalan di port 5000
Secret key : "MyKey123"
Menunggu koneksi dari sender...
(Tekan Ctrl+C untuk menghentikan server)

Sender terhubung dari 127.0.0.1:54321

Menerima pesan dan dapat membalas ('exit' atau 'quit' untuk keluar).

------------------------------------------------------------

   Menunggu pesan dari sender...
   Ciphertext diterima : 72B04E38A3A4D9F8E1293B88...
   Plaintext (dekripsi): "Halo, ini pesan rahasia!"
   Ukuran              : 32 byte -> 24 byte

   [SENDER] > Halo, ini pesan rahasia!

[ANDA] > Pesan diterima dengan baik.
   Plaintext  : "Pesan diterima dengan baik."
   Ciphertext : F4A92B1C...
```

---

## Troubleshooting

| Gejala                            | Penyebab Umum                                                | Tindakan Perbaikan                                                                      |
| --------------------------------- | ------------------------------------------------------------ | --------------------------------------------------------------------------------------- |
| `Address already in use`        | Port masih terikat oleh proses sebelumnya.                   | Ubah nomor port (misal 5001) atau matikan proses lama melalui task manager/`netstat`. |
| `Connection refused`            | Server receiver belum dijalankan atau port salah.            | Jalankan`receiver.py` terlebih dahulu sebelum menjalankan `sender.py`.              |
| `Key harus tepat 8 karakter`    | Input kunci tidak memenuhi syarat 64 bit (8 karakter ASCII). | Masukkan string dengan panjang tepat 8 karakter (contoh:`12345678`).                  |
| Hasil dekripsi gagal / teks rusak | Kunci yang dimasukkan pada sender dan receiver berbeda.      | Pastikan kedua perangkat memasukkan kunci rahasia yang sama persis.                     |
| Paket tidak muncul di Wireshark   | Pemilihan interface capture tidak sesuai.                    | Gunakan Npcap Loopback Adapter jika pengujian dilakukan di localhost.                   |
