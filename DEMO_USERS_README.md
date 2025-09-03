# 🚀 Trailium Demo Kullanıcı Oluşturma Rehberi

Bu rehber, Trailium uygulamasında demo kullanıcıları ve içeriklerini nasıl oluşturacağınızı açıklar.

## 📋 Ön Gereksinimler

1. **Django Backend Server'ı çalışır durumda olmalı**
2. **Virtual Environment aktif olmalı**
3. **Gerekli Python paketleri yüklü olmalı**

## 🛠️ Kurulum

### 1. Backend Server'ı Başlatın
```bash
cd apps/backend
python manage.py runserver
```

### 2. Virtual Environment'ı Aktif Edin
```bash
# macOS/Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

## 🎯 Demo Kullanıcı Oluşturma Yöntemleri

### Yöntem 1: Shell Script (Önerilen - macOS/Linux)
```bash
# Script'i çalıştırılabilir yapın
chmod +x create_demo_users.sh

# Script'i çalıştırın
./create_demo_users.sh
```

### Yöntem 2: Python Script (Tüm Platformlar)
```bash
# Script'i çalıştırılabilir yapın
chmod +x create_demo_users.py

# Script'i çalıştırın
python create_demo_users.py
```

### Yöntem 3: Manuel Django Command
```bash
cd apps/backend

# Sadece admin kullanıcı
python manage.py create_demo_users --admin

# 25 demo kullanıcı + admin
python manage.py create_demo_users --count 25 --admin

# Mevcut kullanıcıları temizle ve yeniden oluştur
python manage.py create_demo_users --count 25 --clear --admin
```

## 📱 Oluşturulan Kullanıcı Bilgileri

### Admin Kullanıcı
- **Kullanıcı Adı:** `emre`
- **Şifre:** `emre`
- **Email:** `emre@trailium.com`
- **Özellikler:** Premium, Admin, Superuser

### Demo Kullanıcılar
- **Şifre:** `demo123` (tüm demo kullanıcılar için)
- **Email:** `[username]@demo.trailium.com`
- **Özellikler:**
  - 30% Premium üye
  - 20% Gizli hesap
  - Gerçekçi Türk isimleri
  - Farklı şehirler ve şirketler

## 🎨 Oluşturulan İçerikler

### 👥 Kullanıcı Profilleri
- **İsimler:** Gerçekçi Türk isimleri (Ahmet Yılmaz, Ayşe Kaya, vb.)
- **Şehirler:** İstanbul, Ankara, İzmir, Bursa, Antalya, vb.
- **Şirketler:** N2Mobil, Garanti BBVA, İş Bankası, vb.
- **Avatar:** DiceBear API ile otomatik avatar

### 📝 Sosyal İçerik
- **Gönderiler:** 1-3 gönderi/kullanıcı
- **Yorumlar:** 0-3 yorum/gönderi
- **Beğeniler:** 0-5 beğeni/gönderi
- **Albümler:** 0-2 albüm/kullanıcı
- **Fotoğraflar:** 1-5 fotoğraf/albüm

### ✅ Todo Listeleri
- **Listeler:** 1-2 liste/kullanıcı
- **Görevler:** 3-8 görev/liste
- **Alt Görevler:** 1-3 alt görev/görev
- **Öncelikler:** Low, Medium, High
- **Tarihler:** Geçmiş ve gelecek tarihler

### 🔗 Takip İlişkileri
- **Takip Sayısı:** 3-8 kullanıcı/kullanıcı
- **Durum:** 80% kabul edilmiş, 20% bekliyor

## 🎛️ Script Parametreleri

### Temel Parametreler
- `--count N`: Kaç demo kullanıcı oluşturulacağı
- `--clear`: Mevcut demo kullanıcıları temizle
- `--admin`: Admin kullanıcı (emre/emre) oluştur

### Örnek Kullanımlar
```bash
# Sadece admin
python manage.py create_demo_users --admin

# 10 demo kullanıcı + admin
python manage.py create_demo_users --count 10 --admin

# 50 demo kullanıcı + admin
python manage.py create_demo_users --count 50 --admin

# Mevcutleri temizle ve 25 yeni oluştur
python manage.py create_demo_users --count 25 --clear --admin
```

## 🔍 Demo Kullanıcıları Görüntüleme

### Django Shell ile
```bash
cd apps/backend
python manage.py shell

# Tüm demo kullanıcıları listele
from users.models import User
demo_users = User.objects.filter(is_staff=False)
for user in demo_users:
    print(f"{user.username}: {user.full_name} ({user.email})")

# Premium kullanıcıları listele
premium_users = User.objects.filter(is_premium=True, is_staff=False)
print(f"Premium kullanıcı sayısı: {premium_users.count()}")

# Gizli hesapları listele
private_users = User.objects.filter(is_private=True, is_staff=False)
print(f"Gizli hesap sayısı: {private_users.count()}")
```

### Admin Panel ile
- URL: `http://127.0.0.1:8000/admin`
- Kullanıcı: `emre`
- Şifre: `emre`

## 🚨 Sorun Giderme

### Hata: "Django server çalışmıyor"
```bash
# Backend server'ı başlatın
cd apps/backend
python manage.py runserver
```

### Hata: "Virtual environment bulunamadı"
```bash
# Virtual environment oluşturun
cd apps/backend
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# veya
.venv\Scripts\activate     # Windows
```

### Hata: "Permission denied"
```bash
# Script'i çalıştırılabilir yapın
chmod +x create_demo_users.sh
chmod +x create_demo_users.py
```

### Hata: "Module not found"
```bash
# Gerekli paketleri yükleyin
cd apps/backend
pip install -r requirements.txt
```

## 📊 Performans Bilgileri

### Oluşturma Süreleri (yaklaşık)
- **10 kullanıcı:** 5-10 saniye
- **25 kullanıcı:** 15-25 saniye
- **50 kullanıcı:** 30-50 saniye

### Veritabanı Boyutu
- **25 kullanıcı:** ~2-5 MB
- **50 kullanıcı:** ~5-10 MB
- **100 kullanıcı:** ~10-20 MB

## 🎯 Özelleştirme

### Yeni İsimler Ekleme
`apps/backend/users/management/commands/create_demo_users.py` dosyasında:

```python
male_names = [
    'Ahmet', 'Mehmet', 'Ali',
    # Yeni isimler ekleyin
    'Yeni_İsim'
]
```

### Yeni Şirketler Ekleme
```python
companies = [
    'N2Mobil', 'Garanti BBVA',
    # Yeni şirketler ekleyin
    'Yeni_Şirket'
]
```

### Yeni Şehirler Ekleme
```python
cities = [
    'İstanbul', 'Ankara', 'İzmir',
    # Yeni şehirler ekleyin
    'Yeni_Şehir'
]
```

## 🔄 Güncelleme

Script'i güncellemek için:
```bash
# Ana dizinde
git pull origin main

# Veya manuel olarak dosyaları güncelleyin
```

## 📞 Destek

Herhangi bir sorun yaşarsanız:
1. Django server'ın çalıştığından emin olun
2. Virtual environment'ın aktif olduğunu kontrol edin
3. Hata mesajlarını dikkatlice okuyun
4. Gerekirse mevcut demo kullanıcıları temizleyin (`--clear` parametresi ile)

---

**🎉 İyi eğlenceler! Trailium demo kullanıcıları ile uygulamanızı test edin!**
