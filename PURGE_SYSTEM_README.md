# 🚨 Purge Non-Admin Users System

Bu sistem, Trailium uygulamasında tüm non-admin kullanıcıları ve ilgili içeriklerini güvenli bir şekilde silmek için tasarlanmıştır.

## 🎯 **Özellikler**

### **Backend (Django)**
- **Management Command**: `purge_non_admin_users`
- **API Endpoint**: `POST /api/admin-tools/purge-non-admin-users/`
- **Güvenlik**: Sadece superuser'lar erişebilir
- **Onay Sistemi**: Tam metin onayı gerekli (`PURGE_NON_ADMIN_USERS`)
- **Dry Run Modu**: Silme işlemi öncesi önizleme
- **Transaction Güvenliği**: Hata durumunda rollback
- **Detaylı Loglama**: Tüm işlemler loglanır

### **Frontend (Vue.js)**
- **Admin Danger Zone Sayfası**: `/admin-danger`
- **Güvenlik Kontrolü**: Sadece superuser'lar erişebilir
- **Dry Run Sonuçları**: Görsel önizleme
- **Onay Modalı**: Çift onay sistemi
- **Responsive Tasarım**: Mobil uyumlu

## 🛡️ **Güvenlik Özellikleri**

1. **Yetki Kontrolü**: Sadece `is_superuser=True` olan kullanıcılar
2. **Onay Metni**: Tam metin onayı gerekli
3. **Transaction**: Tüm işlemler transaction içinde
4. **Loglama**: Tüm işlemler detaylı loglanır
5. **Rate Limiting**: API endpoint'leri korunur

## 📋 **Kullanım**

### **CLI (Management Command)**

#### **Dry Run (Önerilen)**
```bash
cd apps/backend
python manage.py purge_non_admin_users --dry-run --keep=admin
```

#### **Gerçek Silme**
```bash
python manage.py purge_non_admin_users --keep=admin
```

#### **Parametreler**
- `--dry-run`: Sadece önizleme (varsayılan)
- `--keep`: Korunacak kullanıcılar (username veya email)
- `--force`: Onay prompt'unu atla (dikkatli kullanın)

### **API Endpoint**

#### **Dry Run**
```bash
curl -X POST http://localhost:8000/api/admin-tools/purge-non-admin-users/ \
  -H "Authorization: Bearer <ADMIN_ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "confirm": "PURGE_NON_ADMIN_USERS",
    "dry_run": true,
    "keep": ["admin"]
  }'
```

#### **Gerçek Silme**
```bash
curl -X POST http://localhost:8000/api/admin-tools/purge-non-admin-users/ \
  -H "Authorization: Bearer <ADMIN_ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "confirm": "PURGE_NON_ADMIN_USERS",
    "dry_run": false,
    "keep": ["admin"]
  }'
```

### **Frontend**

1. **Admin olarak giriş yapın**
2. **Sidebar'da "🚨 Danger Zone" link'ine tıklayın**
3. **"🔍 Run Dry Run" butonuna tıklayın**
4. **Sonuçları inceleyin**
5. **"🗑️ Execute Purge" butonuna tıklayın**
6. **Onay modalında "PURGE_NON_ADMIN_USERS" yazın**
7. **"Execute Purge" butonuna tıklayın**

## 🔧 **Teknik Detaylar**

### **Silinen İçerikler**
- **Kullanıcılar**: Tüm non-admin kullanıcılar
- **Posts**: Kullanıcı postları
- **Comments**: Yorumlar
- **Likes**: Beğeniler
- **Albums**: Fotoğraf albümleri
- **Photos**: Fotoğraflar
- **Follows**: Takip ilişkileri
- **Todo Lists**: Todo listeleri
- **Todo Items**: Todo öğeleri
- **Todo Sub-Items**: Alt todo öğeleri

### **Korunan İçerikler**
- **Superuser'lar**: `is_superuser=True` olan tüm kullanıcılar
- **Whitelist**: `--keep` parametresi ile belirtilen kullanıcılar

### **Silme Sırası**
1. Follows (PROTECT ilişkileri için)
2. Likes
3. Comments
4. Photos
5. Albums
6. Todo Sub-Items
7. Todo Items
8. Todo Lists
9. Posts
10. Users

## 📊 **Örnek Çıktılar**

### **Dry Run Çıktısı**
```
🔍 DRY RUN MODE - No data will be deleted

📊 WOULD DELETE SUMMARY:
==================================================
👥 Users: 5

📱 Social Content:
  📝 Posts: 8
  💬 Comments: 14
  ❤️  Likes: 13
  📸 Albums: 6
  🖼️  Photos: 15
  🔗 Follows: 0

✅ Todo Content:
  📋 Lists: 6
  ☑️  Items: 27
  🔸 Sub-items: 45

📈 Totals:
  🎯 Total Related Objects: 134
  💾 Total Storage Impact: ~13.4 MB

🛡️  Preserved Users: 1
  📝 Usernames: admin

⚠️  This is a DRY RUN. No data was actually deleted.
To actually delete, run without --dry-run flag.
```

### **API Response (Dry Run)**
```json
{
  "mode": "dry_run",
  "message": "Dry run completed - no data was deleted",
  "would_delete": {
    "users": 5,
    "posts": 8,
    "comments": 14,
    "likes": 13,
    "albums": 6,
    "photos": 15,
    "follows": 0,
    "todo_lists": 6,
    "todo_items": 27,
    "todo_sub_items": 45,
    "kept_users": 1,
    "kept_usernames": ["admin"],
    "total_related": 134
  }
}
```

## ⚠️ **Önemli Notlar**

1. **Geri Alınamaz**: Bu işlem geri alınamaz
2. **Yedekleme**: İşlem öncesi veritabanını yedekleyin
3. **Test**: Önce test ortamında deneyin
4. **Onay**: Her zaman dry run ile başlayın
5. **Yetki**: Sadece gerekli yetkiye sahip kullanıcılar kullanmalı

## 🚀 **Test Senaryoları**

### **Senaryo 1: Dry Run Test**
1. Demo kullanıcılar oluşturun
2. Dry run çalıştırın
3. Sonuçları kontrol edin
4. Veri silinmediğini doğrulayın

### **Senaryo 2: Gerçek Purge Test**
1. Demo kullanıcılar oluşturun
2. Purge işlemini çalıştırın
3. Kullanıcı sayısını kontrol edin
4. İlgili içeriklerin silindiğini doğrulayın

### **Senaryo 3: API Test**
1. Admin token alın
2. Dry run API çağrısı yapın
3. Gerçek purge API çağrısı yapın
4. Sonuçları kontrol edin

### **Senaryo 4: Frontend Test**
1. Admin olarak giriş yapın
2. Admin Danger Zone sayfasına gidin
3. Dry run çalıştırın
4. Purge işlemini test edin

## 🔍 **Troubleshooting**

### **Hata: "Cannot resolve keyword"**
- Model field adlarını kontrol edin
- Migration'ları çalıştırın

### **Hata: "Permission denied"**
- Kullanıcının `is_superuser=True` olduğunu kontrol edin
- Token'ın geçerli olduğunu kontrol edin

### **Hata: "Confirmation required"**
- `confirm` field'ında tam metni yazdığınızdan emin olun
- `"PURGE_NON_ADMIN_USERS"` olarak yazın

## 📝 **Loglar**

Tüm işlemler Django loglarına kaydedilir:

```python
# Dry run log
logger.info(f'PURGE_NON_ADMIN_USERS dry run by {username} ({user_id}) from {ip}')

# Actual purge log
logger.warning(f'PURGE_NON_ADMIN_USERS executed by {username} ({user_id}) from {ip}')
```

## 🎉 **Sonuç**

Bu sistem, Trailium uygulamasında güvenli ve kontrollü kullanıcı temizliği sağlar. Hem CLI hem de API üzerinden kullanılabilir, kapsamlı güvenlik önlemleri içerir ve tüm işlemleri detaylı olarak loglar.

**⚠️ Dikkat**: Bu sistem sadece acil durumlar için kullanılmalıdır. Normal kullanıcı yönetimi için Django Admin veya standart user management araçlarını kullanın.
