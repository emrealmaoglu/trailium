# 🎯 Trailium Özel Kullanıcı Oluşturma Rehberi

Bu rehber, Trailium uygulamasında özel kullanıcıları nasıl oluşturacağınızı açıklar. Script, sizden aldığı bilgilerle kullanıcı ve tüm içeriklerini oluşturur. **Fotoğraflar otomatik olarak [JSONPlaceholder API](https://jsonplaceholder.typicode.com/)'den çekilir.**

## 🚀 **Hızlı Başlangıç**

### 1. **Backend Server'ı Başlatın**
```bash
cd apps/backend
python manage.py runserver
```

### 2. **Script'i Çalıştırın**
```bash
python create_custom_user.py
```

## 📋 **Sizden İsteyeceğim Bilgiler**

### **👤 Kullanıcı Profil Bilgileri**
| Alan | Açıklama | Örnek | Zorunlu |
|------|-----------|--------|----------|
| **Ad Soyad** | Kullanıcının tam adı | "Ahmet Yılmaz" | ✅ |
| **Kullanıcı Adı** | Benzersiz kullanıcı adı | "ahmetyilmaz" | ✅ |
| **Email** | Benzersiz email adresi | "ahmet@example.com" | ✅ |
| **Telefon** | Telefon numarası | "+90 555 123 4567" | ✅ |
| **Şehir** | Yaşadığı şehir | "İstanbul" | ✅ |
| **Şirket** | Çalıştığı şirket | "N2Mobil" | ❌ |
| **Hakkında** | Kısa açıklama | "Yazılım geliştirici" | ❌ |
| **Cinsiyet** | M/F/O | "M" | ✅ |
| **Premium üye mi?** | y/n | "y" | ❌ |
| **Gizli hesap mı?** | y/n | "n" | ❌ |

### **📝 Post İçerikleri**
- **Post sayısı:** 3-5 arası
- **Her post için:**
  - Başlık (örn: "Bugün harika bir gün!")
  - İçerik (örn: "Yeni projeler üzerinde çalışıyorum ve çok heyecanlıyım...")

### **✅ Todo İçerikleri**
- **Todo liste sayısı:** 2-3 arası
- **Her liste için:**
  - Liste başlığı (örn: "Günlük Görevler")
  - 5-8 görev (örn: "E-postaları kontrol et")
  - Her görev için 2-3 alt görev (örn: "Gelen kutusunu temizle")

### **📸 Albüm İçerikleri**
- **Albüm sayısı:** 2-3 arası
- **Her albüm için:**
  - Albüm başlığı (örn: "Tatil Fotoğrafları")
  - 3-5 fotoğraf başlığı (örn: "Sahilde gün batımı")

## 🌟 **Öne Çıkan Özellikler**

### **📸 Cinsiyete Uygun Fotoğraf Seçimi**
Script artık kullanıcının cinsiyetine göre uygun fotoğraflar seçer:

#### **👨 Erkek Kullanıcılar İçin:**
- **Avatar:** Kısa saç, iş/spor temalı, mavi/yeşil tonları
- **Albüm Fotoğrafları:** İş, spor, araba, teknoloji, mimari temalı
- **Renkler:** Mavi, yeşil, gri tonları

#### **👩 Kadın Kullanıcılar İçin:**
- **Avatar:** Uzun saç, moda/güzellik temalı, pembe/mor tonları
- **Albüm Fotoğrafları:** Moda, güzellik, sanat, doğa, çiçek temalı
- **Renkler:** Pembe, mor, altın tonları

#### **⚧ Nötr/Diğer Kullanıcılar İçin:**
- **Avatar:** Kısa saç, genel/soyut temalı, kahverengi/bej tonları
- **Albüm Fotoğrafları:** Soyut, minimal, geometrik, modern, vintage temalı
- **Renkler:** Turuncu, kahverengi, bej tonları

### **🎨 Otomatik Avatar Oluşturma**
- **DiceBear API** ile cinsiyete uygun avatarlar
- **Saç stili, renk, kıyafet** cinsiyete göre ayarlanır
- **Tutarlı görünüm** için seed kullanımı

### **🔄 Akıllı Fallback Sistemi**
- **JSONPlaceholder API** birincil kaynak
- **Picsum Photos** yedek kaynak
- **Cinsiyete uygun renkler** her durumda korunur

## 🎨 **Otomatik Oluşturulan İçerikler**

### **📸 Fotoğraflar**
- **Profil fotoğrafı:** JSONPlaceholder API'den otomatik
- **Albüm fotoğrafları:** Her albüm için JSONPlaceholder API'den
- **Fallback:** Picsum Photos (JSONPlaceholder erişilemezse)

### **🔗 Sosyal Etkileşimler**
- **Beğeniler:** Diğer kullanıcılardan rastgele
- **Yorumlar:** Diğer kullanıcılardan rastgele
- **Takip ilişkileri:** Diğer kullanıcılarla otomatik

### **📅 Tarihler**
- **Oluşturma tarihleri:** Son 30 gün içinde rastgele
- **Bitiş tarihleri:** Gelecek 30 gün içinde rastgele

## 🛠️ **Kullanım Örnekleri**

### **Örnek 1: Basit Kullanıcı**
```bash
python create_custom_user.py
```

**Girilen Bilgiler:**
- Ad Soyad: "Mehmet Demir"
- Kullanıcı Adı: "mehmetdemir"
- Email: "mehmet@demo.com"
- Telefon: "+90 555 987 6543"
- Şehir: "Ankara"
- Cinsiyet: "M"
- Post sayısı: 3
- Todo liste sayısı: 2
- Albüm sayısı: 2

### **Örnek 2: Premium Kullanıcı**
```bash
python create_custom_user.py
```

**Girilen Bilgiler:**
- Ad Soyad: "Ayşe Kaya"
- Kullanıcı Adı: "aysekaya"
- Email: "ayse@premium.com"
- Telefon: "+90 555 111 2222"
- Şehir: "İzmir"
- Şirket: "TechCorp"
- Hakkında: "Senior Developer, React ve Vue.js uzmanı"
- Cinsiyet: "F"
- Premium üye mi?: "y"
- Post sayısı: 5
- Todo liste sayısı: 3
- Albüm sayısı: 3

## 🔧 **Teknik Detaylar**

### **📸 Cinsiyete Uygun Fotoğraf Seçimi**
```python
# Cinsiyete göre fotoğraf kategorileri
if gender == 'M':
    # Erkekler için: iş, spor, araba, teknoloji temalı
    photo_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
elif gender == 'F':
    # Kadınlar için: moda, güzellik, sanat, doğa temalı
    photo_ids = [21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40]
else:
    # Nötr/Diğer için: genel, soyut, mimari temalı
    photo_ids = [41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60]
```

### **👤 Cinsiyete Uygun Avatar Seçimi**
```python
# Erkekler için
"https://api.dicebear.com/7.x/avataaars/svg?seed=male1&backgroundColor=b6e3f4&hair=short&hairColor=black&accessories=round&clothingColor=blue"

# Kadınlar için
"https://api.dicebear.com/7.x/avataaars/svg?seed=female1&backgroundColor=ffb6c1&hair=long&hairColor=black&accessories=round&clothingColor=pink"

# Nötr için
"https://api.dicebear.com/7.x/avataaars/svg?seed=neutral1&backgroundColor=deb887&hair=short&hairColor=brown&accessories=round&clothingColor=brown"
```

### **JSONPlaceholder API Kullanımı**
```python
# Cinsiyete uygun fotoğraf çekme
response = requests.get(f"https://jsonplaceholder.typicode.com/photos/{photo_id}")
if response.status_code == 200:
    photo = response.json()
    return {
        'url': photo['url'],
        'thumbnailUrl': photo['thumbnailUrl']
    }
```

### **Django Management Command**
```bash
python manage.py create_custom_user \
    --username="ahmetyilmaz" \
    --email="ahmet@example.com" \
    --full_name="Ahmet Yılmaz" \
    --phone="+90 555 123 4567" \
    --city="İstanbul" \
    --gender="M" \
    --avatar_url="https://api.dicebear.com/7.x/avataaars/svg?seed=male1&backgroundColor=b6e3f4"
```

## 📱 **Oluşturulan Kullanıcı Bilgileri**

### **Giriş Bilgileri**
- **Kullanıcı Adı:** Sizin girdiğiniz username
- **Şifre:** `demo123` (varsayılan)
- **Email:** Sizin girdiğiniz email

### **Profil Özellikleri**
- **Avatar:** JSONPlaceholder API'den otomatik
- **Adres:** `[Şehir], Türkiye` formatında
- **Hakkında:** Otomatik oluşturulur (boşsa)
- **Premium:** Belirttiğiniz değer
- **Gizli:** Belirttiğiniz değer

## 🚨 **Sorun Giderme**

### **Hata: "Django server çalışmıyor"**
```bash
# Backend server'ı başlatın
cd apps/backend
python manage.py runserver
```

### **Hata: "User already exists"**
```bash
# Farklı username/email kullanın
# Veya mevcut kullanıcıyı silin
```

### **Hata: "Module not found"**
```bash
# Gerekli paketleri yükleyin
cd apps/backend
pip install -r requirements.txt
```

### **Hata: "Permission denied"**
```bash
# Script'i çalıştırılabilir yapın
chmod +x create_custom_user.py
```

## 💡 **İpuçları**

### **İyi Kullanıcı Adları**
- ✅ `ahmetyilmaz`, `aysekaya`, `mehmetdemir`
- ❌ `ahmet`, `ayse`, `mehmet` (çok genel)

### **İyi Post İçerikleri**
- ✅ "Bugün harika bir gün! ☀️"
- ✅ "Yeni projeler üzerinde çalışıyorum 💻"
- ❌ "Test post" (çok basit)

### **İyi Todo İçerikleri**
- ✅ "E-postaları kontrol et"
- ✅ "Proje sunumunu hazırla"
- ❌ "Todo 1" (çok basit)

### **İyi Albüm İçerikleri**
- ✅ "Tatil Fotoğrafları"
- ✅ "İş Toplantıları"
- ❌ "Albüm 1" (çok basit)

## 🔄 **Güncelleme ve Özelleştirme**

### **Script'i Güncelleme**
```bash
# Ana dizinde
git pull origin main

# Veya manuel olarak dosyaları güncelleyin
```

### **Yeni Özellikler Ekleme**
`create_custom_user.py` dosyasında:
```python
# Yeni alan ekleme
user_data['new_field'] = input("Yeni Alan: ").strip()

# Yeni içerik türü ekleme
def get_new_content_input():
    # Yeni içerik türü için input alma
    pass
```

## 📊 **Performans Bilgileri**

### **Oluşturma Süreleri**
- **Basit kullanıcı (3 post, 2 todo, 2 albüm):** 5-10 saniye
- **Orta kullanıcı (5 post, 3 todo, 3 albüm):** 10-15 saniye
- **Karmaşık kullanıcı (5 post, 3 todo, 3 albüm, çok görev):** 15-25 saniye

### **Veritabanı Boyutu**
- **Her kullanıcı:** ~100-500 KB
- **Fotoğraflar:** JSONPlaceholder API'den (veritabanında saklanmaz)

## 🌐 **API Referansları**

### **JSONPlaceholder API**
- **Ana URL:** https://jsonplaceholder.typicode.com/
- **Fotoğraflar:** https://jsonplaceholder.typicode.com/photos
- **Kullanıcılar:** https://jsonplaceholder.typicode.com/users
- **Gönderiler:** https://jsonplaceholder.typicode.com/posts

### **Fallback API (Picsum Photos)**
- **Ana URL:** https://picsum.photos/
- **Rastgele:** https://picsum.photos/400/300?random=1

## 📞 **Destek**

Herhangi bir sorun yaşarsanız:
1. Django server'ın çalıştığından emin olun
2. Virtual environment'ın aktif olduğunu kontrol edin
3. Hata mesajlarını dikkatlice okuyun
4. JSONPlaceholder API'nin erişilebilir olduğunu kontrol edin

---

**🎉 İyi eğlenceler! Özel kullanıcılarınızla Trailium'u test edin!**

**📸 Fotoğraflar otomatik olarak [JSONPlaceholder](https://jsonplaceholder.typicode.com/) API'den çekilecek!**
