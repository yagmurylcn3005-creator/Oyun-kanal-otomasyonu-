# Yerel AI oyun kanalı içerik otomasyonu

Oyun adı ve birkaç tercih vererek **yerel Ollama modeliyle** video planı, Türkçe seslendirme taslağı ve YouTube metadata'sı hazırlayın. Üretilen her paket otomatik olarak yeni bir klasöre kaydedilir. Gemini/API anahtarı gerekmez; Ollama erişilemiyorsa uygulama bunu belirtip çevrimdışı şablonla devam eder.

> Bu araç içerik paketi hazırlar; oyun görüntüsü kaydetmez, videoyu render etmez ve YouTube'a yüklemez. Oynanış görüntülerinizi ve kişisel deneyiminizi scriptteki ilgili yerlere ekleyin.

## Gereksinimler

- Python 3.10 veya üzeri
- [Ollama](https://ollama.com/download) (gerçek yerel AI üretimi için)
- Model için yeterli disk/RAM; ilk model indirmesi internet bağlantısı gerektirir. Sonraki üretimler yerel çalışır.

## Tek seferlik kurulum

Proje klasöründe terminal açın:

```bash
python -m venv .venv
# Windows PowerShell:
.venv\\Scripts\\Activate.ps1
# macOS/Linux için bunun yerine: source .venv/bin/activate
python -m pip install -r requirements.txt
ollama pull qwen2.5:7b
```

Ollama masaüstü uygulamasını açık tutun. Gerekirse ayrı terminalde `ollama serve` çalıştırın. `.env.example` dosyasını `.env` olarak kopyalamak zorunlu değildir; varsayılan ayarlar Ollama'yı `http://localhost:11434` ve `qwen2.5:7b` üzerinde arar. Ayar değiştirmek için `.env.example` dosyasını `.env` olarak kopyalayıp `OLLAMA_MODEL`, `OLLAMA_BASE_URL` veya `USE_LOCAL_LLM` değerlerini düzenleyin.

Daha düşük donanım için Ollama'da mevcut daha küçük bir model kullanın, örneğin `ollama pull qwen2.5:3b`, ardından `.env` içinde `OLLAMA_MODEL=qwen2.5:3b` ayarlayın.

## Her video için tek komut

```bash
python video_workflow.py --game "Elden Ring" --platform "PC" --style "analitik" --tone "samimi ve heyecanlı" --duration 10
```

Her çalıştırmada `output/elden-ring-YYYYMMDD-HHMMSS/` benzeri yeni bir klasör oluşur:

- `plan.json` — makine tarafından okunabilir plan ve üretim kaynağı
- `summary.md` — plan, akış, görüntü planı ve script
- `script.txt` — seslendirme/video scripti
- `youtube_meta.txt` — başlık, açıklama, etiketler ve hashtagler
- `youtube_meta.json` — metadata'nın JSON biçimi

Örnekler:

```bash
python video_workflow.py --game "CS2" --platform "PC" --duration 8
python video_workflow.py --game "Zelda" --platform "Switch" --mode script
python app.py --game "Stardew Valley" --style "sakin" --json
python video_workflow.py --game "Fortnite" --no-save
```

`--mode` terminalde hangi çıktının gösterileceğini belirler; varsayılan `all`'dır. Dosyalar varsayılan olarak her modda kaydedilir. `--output-dir taslaklar` kayıt konumunu değiştirir. `--no-save` yalnızca terminal çıktısı verir.

## Tamamen şablonla çalışma

Ollama kullanmadan çevrimdışı şablon üretmek için `.env` ayarına `USE_LOCAL_LLM=false` ekleyin. Ollama açıksa varsayılan olarak yerel model kullanılır; bağlantı/model hatasında uygulama uyarı verir ve şablonla içerik paketini yine de kaydeder. Bulut API'ye otomatik fallback yapılmaz.

## Testler

```bash
python -m pytest -q
```
