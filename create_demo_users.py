#!/usr/bin/env python3
"""
Trailium Demo Kullanıcı Oluşturma Script'i
Bu script demo kullanıcıları ve içeriklerini oluşturur
"""

import os
import sys
import subprocess
import requests
import time

def print_header():
    print("🚀 Trailium Demo Kullanıcı Oluşturma Script'i")
    print("=" * 50)
    print()

def check_django_server():
    """Django server'ın çalışıp çalışmadığını kontrol et"""
    print("🔍 Django server kontrol ediliyor...")

    try:
        response = requests.get("http://127.0.0.1:8000/api/health/", timeout=5)
        if response.status_code == 200:
            print("✅ Django server çalışıyor!")
            return True
    except requests.exceptions.RequestException:
        pass

    print("❌ Django server çalışmıyor!")
    print("   Lütfen önce server'ı başlatın:")
    print("   cd apps/backend && python manage.py runserver")
    return False

def run_django_command(command):
    """Django management command'ı çalıştır"""
    backend_dir = os.path.join(os.getcwd(), "apps", "backend")

    if not os.path.exists(backend_dir):
        print(f"❌ Backend dizini bulunamadı: {backend_dir}")
        return False

    try:
        # Backend dizinine git
        os.chdir(backend_dir)

        # Virtual environment'ı kontrol et
        venv_paths = [".venv", "venv"]
        venv_activated = False

        for venv_path in venv_paths:
            if os.path.exists(venv_path):
                if sys.platform == "win32":
                    activate_script = os.path.join(venv_path, "Scripts", "activate.bat")
                    if os.path.exists(activate_script):
                        os.environ["VIRTUAL_ENV"] = os.path.abspath(venv_path)
                        venv_activated = True
                        break
                else:
                    activate_script = os.path.join(venv_path, "bin", "activate")
                    if os.path.exists(activate_script):
                        os.environ["VIRTUAL_ENV"] = os.path.abspath(venv_path)
                        venv_activated = True
                        break

        if venv_activated:
            print("📦 Virtual environment aktif edildi")

        # Django command'ı çalıştır
        result = subprocess.run(
            ["python", "manage.py"] + command.split(),
            capture_output=True,
            text=True,
            cwd=backend_dir
        )

        if result.returncode == 0:
            print(result.stdout)
            return True
        else:
            print(f"❌ Hata: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Hata oluştu: {e}")
        return False
    finally:
        # Ana dizine geri dön
        os.chdir(os.path.dirname(os.path.dirname(backend_dir)))

def show_menu():
    """Ana menüyü göster"""
    print("📋 Demo kullanıcı oluşturma seçenekleri:")
    print("1. Sadece admin kullanıcı oluştur (emre/emre)")
    print("2. 10 demo kullanıcı oluştur")
    print("3. 25 demo kullanıcı oluştur (varsayılan)")
    print("4. 50 demo kullanıcı oluştur")
    print("5. Mevcut demo kullanıcıları temizle ve yeniden oluştur")
    print("6. Özel sayıda demo kullanıcı oluştur")
    print("7. Çıkış")
    print()

def get_user_choice():
    """Kullanıcı seçimini al"""
    while True:
        try:
            choice = input("Seçiminizi yapın (1-7): ").strip()
            if choice in ['1', '2', '3', '4', '5', '6', '7']:
                return choice
            else:
                print("❌ Lütfen 1-7 arasında bir sayı girin!")
        except KeyboardInterrupt:
            print("\n\n👋 Görüşürüz!")
            sys.exit(0)

def execute_choice(choice):
    """Seçilen işlemi gerçekleştir"""
    if choice == '1':
        print("👑 Admin kullanıcı oluşturuluyor...")
        return run_django_command("create_demo_users --admin")

    elif choice == '2':
        print("👥 10 demo kullanıcı oluşturuluyor...")
        return run_django_command("create_demo_users --count 10 --admin")

    elif choice == '3':
        print("👥 25 demo kullanıcı oluşturuluyor...")
        return run_django_command("create_demo_users --count 25 --admin")

    elif choice == '4':
        print("👥 50 demo kullanıcı oluşturuluyor...")
        return run_django_command("create_demo_users --count 50 --admin")

    elif choice == '5':
        print("🧹 Mevcut demo kullanıcılar temizleniyor ve yeniden oluşturuluyor...")
        return run_django_command("create_demo_users --count 25 --clear --admin")

    elif choice == '6':
        try:
            custom_count = int(input("Kaç demo kullanıcı oluşturmak istiyorsunuz? "))
            if custom_count <= 0:
                print("❌ Pozitif bir sayı girin!")
                return False
            print(f"👥 {custom_count} demo kullanıcı oluşturuluyor...")
            return run_django_command(f"create_demo_users --count {custom_count} --admin")
        except ValueError:
            print("❌ Geçerli bir sayı girin!")
            return False

    elif choice == '7':
        print("👋 Görüşürüz!")
        sys.exit(0)

def show_success_info():
    """Başarı bilgilerini göster"""
    print()
    print("✅ Demo kullanıcılar başarıyla oluşturuldu!")
    print()
    print("📱 Giriş bilgileri:")
    print("   Admin: emre / emre")
    print("   Demo kullanıcılar: [username] / demo123")
    print()
    print("🌐 Uygulamayı test etmek için: http://localhost:5173")
    print("🔧 Admin paneli: http://127.0.0.1:8000/admin")
    print()
    print("💡 İpucu: Demo kullanıcıların kullanıcı adlarını görmek için:")
    print("   cd apps/backend")
    print("   python manage.py shell")
    print("   from users.models import User; [u.username for u in User.objects.filter(is_staff=False)]")

def main():
    """Ana fonksiyon"""
    print_header()

    # Django server kontrolü
    if not check_django_server():
        return

    print()

    while True:
        show_menu()
        choice = get_user_choice()

        if choice == '7':
            break

        print()
        success = execute_choice(choice)

        if success:
            show_success_info()
        else:
            print("❌ Demo kullanıcılar oluşturulamadı!")

        print()
        input("Devam etmek için Enter'a basın...")
        print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Görüşürüz!")
        sys.exit(0)
