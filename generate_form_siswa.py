"""Generator data sintetis umpan balik siswa (gaya isian Google Forms/LMS) untuk 6 kelas emosi belajar.

Output (folder analisis-sentimen-siswa/):
  <Kelas>Form.csv          -> data sintetis per emosi (kolom Tweet, Label, Sumber)
  DatasetFinal.csv         -> gabungan data sintetis + data hasil filter dari internet
CATATAN: data sintetis perlu dikombinasikan dengan data asli siswa & diverifikasi anotator.
"""
import random
import re
from pathlib import Path

import pandas as pd

random.seed(2026)
OUT = Path(__file__).parent / "analisis-sentimen-siswa"
N_PER_CLASS = 3000

MEDIA = ["video pembelajaran", "materi di Google Classroom", "kuis online", "slide PPT", "aplikasi belajar",
         "pembelajaran lewat zoom", "LKPD digital", "simulasi PhET", "modul elektronik", "Quizizz", "Kahoot",
         "e-learning sekolah", "video YouTube dari guru", "materi di LMS", "tugas online", "diskusi di grup kelas",
         "praktikum virtual", "flashcard digital", "e-book pelajaran", "latihan soal di aplikasi"]
MAPEL = ["matematika", "fisika", "kimia", "biologi", "bahasa inggris", "sejarah", "ekonomi", "informatika",
         "IPA", "IPS", "bahasa Indonesia", "PKN", "geografi", "sosiologi", "seni budaya", "statistika"]
TOPIK = ["trigonometri", "hukum Newton", "stoikiometri", "sistem pencernaan", "present tense", "perang dunia",
         "permintaan dan penawaran", "algoritma dasar", "persamaan kuadrat", "ekosistem", "teks eksposisi",
         "peta konsep", "listrik dinamis", "tabel periodik", "fungsi eksponen", "pasar modal", "limit fungsi"]

PREFIX = ["", "", "", "jujur ", "sejujurnya ", "menurut saya ", "kalau saya sih ", "pas tadi ", "hari ini ",
          "terus terang ", "dari pengalaman saya ", "jujur aja ", "honestly ", "setelah belajar ", "tadi pagi "]
SUFFIX = ["", "", "", ".", " sih", " banget", " pokoknya", " menurutku", " wkwk", " hehe", " jujur", " deh",
          " kak", " pak/bu", " buat saya", " untuk saya pribadi", " secara keseluruhan"]

# {m}=media, {p}=mapel, {t}=topik
E = {
 "Senang": [
  "aku senang banget belajar {p} pakai {m}", "belajar {t} lewat {m} jadi menyenangkan", "saya puas sama {m} hari ini",
  "alhamdulillah {m} nya bagus dan gampang dipahami", "seneng deh akhirnya paham {t}", "{m} nya bikin aku nyaman belajar {p}",
  "hari ini belajarnya menyenangkan, {m} nya jelas", "senang sekali bisa ngerjain {m} dengan lancar",
  "bahagia banget nilai kuis {p} ku bagus", "lega dan senang karena {t} sudah ngerti sekarang",
  "{m} hari ini bikin suasana kelas jadi happy", "aku merasa tenang dan senang pas pakai {m}",
  "tampilan {m} nya enak dilihat, aku suka", "penjelasan {t} di {m} runtut jadi saya senang belajarnya",
  "puas banget sama hasil belajar {p} lewat {m}", "belajar {p} sekarang nggak seberat dulu, aku senang",
  "senang karena guru menjelaskan {t} dengan {m} yang menarik", "rasanya happy bisa menyelesaikan {m} tepat waktu",
  "terhibur banget sama {m} hari ini", "aku bersyukur ada {m}, belajar {p} jadi lebih mudah dan menyenangkan"],
 "Antusias": [
  "aku semangat banget belajar {p} pakai {m}", "nggak sabar pengen coba {m} lagi besok", "penasaran banget sama lanjutan {t}, pengen cepat belajar lagi",
  "seru banget {m} nya, jadi pengen belajar lebih banyak", "antusias banget ikut {m} hari ini", "aku excited banget buat {t}",
  "pengen langsung praktik {t} setelah lihat {m}", "ayo kita bahas {t} lebih dalam lagi besok", "{m} nya bikin aku termotivasi buat belajar {p}",
  "gak sabar nunggu pertemuan {p} berikutnya", "semangat ngerjain {m}, pengen dapet nilai tinggi", "pengen banget eksplor {m} lebih jauh",
  "tertantang banget sama soal {t}, pengen cepat nyoba", "{m} hari ini bikin semangat belajarku naik", "aku jadi bersemangat belajar {p} setelah pakai {m}",
  "pengen cepat-cepat buka {m} lagi buat belajar {t}", "wah {t} seru banget, aku pengen tahu lebih banyak", "ketagihan ngerjain {m}, semangat terus!",
  "besok aku mau coba {m} lagi, nggak sabar", "kepo banget sama materi {t} berikutnya, semoga cepat dibahas"],
 "Netral": [
  "hari ini belajar {p} menggunakan {m}", "materi yang dibahas adalah {t}", "durasi {m} sekitar sepuluh menit",
  "tugas {p} dikumpulkan lewat {m}", "pembelajaran {p} dilaksanakan secara daring hari ini", "{m} dibuka pukul tujuh pagi",
  "saya mengerjakan {m} di rumah", "guru menjelaskan {t} lalu memberi {m}", "ada tiga bagian dalam {m} hari ini",
  "pertemuan {p} dibagi menjadi dua sesi", "saya mengakses {m} lewat laptop", "kuis {p} berisi sepuluh soal",
  "jadwal {p} hari ini setelah istirahat", "{m} nya sudah saya buka dan saya baca", "topik minggu ini {t}",
  "saya belajar {t} dari {m} kemarin", "pembelajaran berlangsung seperti biasa", "tidak ada kendala atau hal khusus pada {m}",
  "{m} dipakai untuk membahas {t}", "saya sudah mengisi form refleksi {p} hari ini"],
 "Bingung": [
  "aku bingung sama {t} di {m} nya", "kurang paham bagian {t}, penjelasannya loncat-loncat", "nggak ngerti maksud soal {t} di {m}",
  "materi {t} bikin saya bingung harus mulai dari mana", "belum paham cara pakai {m}, tombolnya banyak banget", "penjelasan {t} kurang jelas jadi saya bingung",
  "saya masih ragu apakah jawaban {t} saya sudah benar", "instruksi di {m} ambigu, saya bingung maksudnya apa", "bingung kenapa hasil {t} ku beda sama contoh",
  "gak paham rumus {t} dipakai di bagian mana", "kok bisa jawabannya begitu ya? aku belum ngerti {t}", "kurang ngerti alur belajar {p} di {m}",
  "masih bingung bedain konsep {t} sama materi sebelumnya", "{m} nya membingungkan, aku nggak tau harus klik yang mana",
  "pas lihat {m} aku malah makin bingung soal {t}", "belum ngerti kenapa langkah {t} nya seperti itu", "saya tidak paham contoh {t} yang diberikan",
  "bingung banget sama urutan materi {p}, kurang runtut", "maksud pertanyaan di {m} itu apa sih? aku kurang paham", "gimana caranya ngerjain {t}? penjelasan di {m} belum bikin paham"],
 "Bosan": [
  "bosan banget belajar {p} pakai {m}", "{m} nya monoton, bikin ngantuk", "jenuh liat slide {p} yang itu-itu aja",
  "boring banget {m} hari ini", "pembelajaran {p} lewat {m} garing dan membosankan", "lama-lama bosen ngerjain {m} terus",
  "ngantuk banget dengerin penjelasan {t} yang panjang", "{m} nya datar banget, nggak ada yang menarik", "suntuk deh belajar {p} online terus",
  "tiap hari {m} nya sama aja, bosen", "materi {t} disampaikan monoton jadi bikin ngantuk", "gak seru banget {m} nya, cuma baca teks doang",
  "bete ngerjain {m} yang gitu-gitu terus", "rasanya jenuh belajar {p} lewat layar seharian", "{m} nya kurang variatif jadi cepat bosen",
  "males fokus karena {m} nya bikin bosen", "pengen belajar {p} dengan cara yang lebih seru, ini udah bosen", "video {t} nya kepanjangan dan membosankan",
  "bosen denger penjelasan {t} yang itu-itu lagi", "pelajaran {p} lewat {m} bikin ngantuk dan jenuh"],
 "Frustrasi": [
  "frustrasi banget, {m} nya error terus", "aku stres ngerjain {t}, udah dicoba berkali-kali tetap salah", "capek banget {m} nya sering eror dan hilang datanya",
  "kesel parah soal {t} nggak ada yang bener", "udah mau nyerah belajar {p} lewat {m}", "pusing banget tugas {p} numpuk dan {m} nya lemot",
  "putus asa deh, {t} nggak masuk-masuk di otak", "jengkel karena {m} gak bisa dibuka padahal deadline dekat", "muak sama {m} yang loading terus",
  "tertekan banget sama tugas {p}, waktu mepet dan {m} bermasalah", "sebel jawaban {t} udah bener tapi dibilang salah sama sistem {m}",
  "{m} nya ngeselin banget, upload tugas gagal terus", "udah capek-capek ngerjain {t} malah ke-submit gagal, frustrasi", "emosi banget jaringan putus pas ngerjain {m}",
  "mumet ngerjain {t}, gak bisa-bisa dari tadi", "nggak kuat lagi sama beban tugas {p} dan {m} yang ribet", "gagal terus ngerjain kuis {t}, bikin frustasi",
  "stress banget {m} logout sendiri pas mau kirim jawaban", "kesal, sudah belajar {t} lama tapi nilainya tetap jelek", "susah banget {t} nya, rasanya mau nyerah aja"],
}

SLANG = [(r"\bbanget\b", "bgt"), (r"\bnggak\b", "ga"), (r"\byang\b", "yg"), (r"\bsudah\b", "udah"),
         (r"\bjuga\b", "jg"), (r"\btidak\b", "gak"), (r"\bsaya\b", "aku"), (r"\bsama\b", "sm"),
         (r"\bkarena\b", "krn"), (r"\bdengan\b", "dg")]


def noise(s):
    r = random.random()
    if r < 0.30:
        for pat, rep in random.sample(SLANG, k=random.randint(1, 3)):
            s = re.sub(pat, rep, s)
    if random.random() < 0.10:  # typo: hapus satu huruf
        i = random.randrange(2, len(s) - 2)
        s = s[:i] + s[i + 1:]
    if random.random() < 0.20:
        s = s + random.choice([" :)", "!!", "...", " hehe", " huhu", " 😅", " 🙏"]) if False else s + random.choice(["!!", "...", " hehe", " huhu"])
    return s


def gen(label):
    seen, rows, tries = set(), [], 0
    while len(rows) < N_PER_CLASS and tries < 50000:
        tries += 1
        core = random.choice(E[label]).format(m=random.choice(MEDIA), p=random.choice(MAPEL), t=random.choice(TOPIK))
        s = (random.choice(PREFIX) + core + random.choice(SUFFIX)).strip().lower()
        s = noise(s)
        if s not in seen:
            seen.add(s)
            rows.append({"Tweet": s, "Label": label, "Sumber": "Sintetis-Form"})
    return pd.DataFrame(rows)


frames = []
for lab in E:
    df = gen(lab)
    df.to_csv(OUT / f"{lab}Form.csv", sep="\t", index=False)
    frames.append(df)
    print(lab, len(df))

_prev = pd.read_csv(OUT / "DatasetFinal.csv", sep="\t")
real = _prev[_prev["Sumber"] != "Sintetis-Form"]  # baris hasil filter dataset internet
final = pd.concat([real] + frames, ignore_index=True).drop_duplicates("Tweet").sample(frac=1, random_state=7)
final.to_csv(OUT / "DatasetFinal.csv", sep="\t", index=False)
print(final.groupby("Label").size())
