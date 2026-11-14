# Yerel AI oyun kanalı içerik otomasyonu

Uygulama artık soru sormadan kendi konu havuzundan sıradaki oyunu seçebilir, yerel Ollama modeliyle Türkçe içerik paketi üretir ve dosyalara kaydeder. Ollama kullanılamazsa hata verip durmak yerine offline şablona geçer. Bulut API veya Gemini anahtarı kullanılmaz.

> Otomasyon içerik taslağı üretir. Oyun görüntüsü kaydetme, gerçek oynanışı doğrulama, ses üretme, video render etme ve YouTube'a yükleme yapmaz. Bunlar mevcut projede bağlı olmayan sistemlerdir; yanlış/deneyimlenmemiş oyun iddialarını yayınlamamak için üretilen içerik taslak olarak kalır.

## İlk kurulum

Python 3.10+ ve [Ollama](https://ollama.com/download) kurun. İlk model indirmesi internet gerektirir; sonrasındaki model çağrıları yerel çalışır.

```bash
python -m venv .venv
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
ollama pull qwen2.5:7b
```

Ollama'yı açık tutun (`ollama serve` gerekebilir). Varsayılanlar `http://localhost:11434` ve `qwen2.5:7b`; `.env.example` dosyasını `.env` olarak kopyalamak zorunlu değildir.

## Soru sormadan otomatik üretim

Proje klasöründe şu komut varsayılan konu listesinden daha önce en uzun süredir üretilmeyen oyunu seçer, içerik paketini oluşturur ve `output/` altına kaydeder:

```bash
python video_workflow.py
```

Otonom biçimde her 24 saatte bir yeni paket oluşturup devam etmesi için:

```bash
python video_workflow.py --watch
```

Durdurmak için `Ctrl+C`. Aralık ve konu havuzu özelleştirilebilir:

```bash
python video_workflow.py --watch --interval-hours 12
```

`autopilot_topics.json` dosyasın�� düzenleyerek oyunları, platformları, stilleri, tonları ve süreleri kendi kanalınıza göre belirleyin. Sıra bilgisi `output/.autopilot_state.json` içinde tutulur; bu dosyayı silerseniz konu rotasyonu baştan başlar. Hatalı veya eksik konu dosyası uygulamayı durdurmaz, yerleşik varsayılan listeyi kullanır.

Her üretim kendi klasörüne şunları kaydeder:

- `plan.json` — plan ve üretim kaynağı
- `summary.md` — içerik özeti, akış ve görüntü önerileri
- `script.txt` — seslendirme taslağı
- `youtube_meta.txt` ve `youtube_meta.json` — başlık, açıklama, etiketler ve hashtagler

Elle oyun seçimi de kullanılabilir:

```bash
python video_workflow.py --game "Elden Ring" --platform "PC" --duration 10
```

Otomasyon internette trend araştırması yapmaz; oyunları yerel listedeki dönüş sırasına göre seçer. Gerçek oynanış görüntüsü, kişisel deneyim ve güncel bilgiler üretici tarafından eklenip kontrol edilmelidir. Sistem otomatik olarak hiçbir şeyi YouTube'a yüklemez veya yayımlamaz.

## Testler

```bash
python -m pytest -q
```
