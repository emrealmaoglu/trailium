#!/bin/bash

# Trailium Demo Kullanıcı Oluşturma Script'i
# Bu script demo kullanıcıları ve içeriklerini oluşturur

echo "🚀 Trailium Demo Kullanıcı Oluşturma Script'i"
echo "================================================"

# Backend dizinine git
cd apps/backend

# Virtual environment'ı aktif et (eğer varsa)
if [ -d ".venv" ]; then
    echo "📦 Virtual environment aktif ediliyor..."
    source .venv/bin/activate
elif [ -d "venv" ]; then
    echo "📦 Virtual environment aktif ediliyor..."
    source venv/bin/activate
fi

# Django server'ın çalışıp çalışmadığını kontrol et
echo "🔍 Django server kontrol ediliyor..."
if ! curl -s http://127.0.0.1:8000/api/health/ > /dev/null; then
    echo "❌ Django server çalışmıyor! Lütfen önce server'ı başlatın:"
    echo "   python manage.py runserver"
    exit 1
fi

echo "✅ Django server çalışıyor!"

# Kullanıcı seçeneklerini göster
echo ""
echo "📋 Demo kullanıcı oluşturma seçenekleri:"
echo "1. Sadece admin kullanıcı oluştur (emre/emre)"
echo "2. 10 demo kullanıcı oluştur"
echo "3. 25 demo kullanıcı oluştur (varsayılan)"
echo "4. 50 demo kullanıcı oluştur"
echo "5. Mevcut demo kullanıcıları temizle ve yeniden oluştur"
echo "6. Özel sayıda demo kullanıcı oluştur"
echo ""

read -p "Seçiminizi yapın (1-6): " choice

case $choice in
    1)
        echo "👑 Admin kullanıcı oluşturuluyor..."
        python manage.py create_demo_users --admin
        ;;
    2)
        echo "👥 10 demo kullanıcı oluşturuluyor..."
        python manage.py create_demo_users --count 10 --admin
        ;;
    3)
        echo "👥 25 demo kullanıcı oluşturuluyor..."
        python manage.py create_demo_users --count 25 --admin
        ;;
    4)
        echo "👥 50 demo kullanıcı oluşturuluyor..."
        python manage.py create_demo_users --count 50 --admin
        ;;
    5)
        echo "🧹 Mevcut demo kullanıcılar temizleniyor ve yeniden oluşturuluyor..."
        python manage.py create_demo_users --count 25 --clear --admin
        ;;
    6)
        read -p "Kaç demo kullanıcı oluşturmak istiyorsunuz? " custom_count
        echo "👥 $custom_count demo kullanıcı oluşturuluyor..."
        python manage.py create_demo_users --count $custom_count --admin
        ;;
    *)
        echo "❌ Geçersiz seçim! Varsayılan olarak 25 demo kullanıcı oluşturuluyor..."
        python manage.py create_demo_users --count 25 --admin
        ;;
esac

echo ""
echo "✅ Demo kullanıcılar başarıyla oluşturuldu!"
echo ""
echo "📱 Giriş bilgileri:"
echo "   Admin: emre / emre"
echo "   Demo kullanıcılar: [username] / demo123"
echo ""
echo "🌐 Uygulamayı test etmek için: http://localhost:5173"
echo "🔧 Admin paneli: http://127.0.0.1:8000/admin"
echo ""
echo "💡 İpucu: Demo kullanıcıların kullanıcı adlarını görmek için:"
echo "   python manage.py shell"
echo "   from users.models import User; [u.username for u in User.objects.filter(is_staff=False)]"
