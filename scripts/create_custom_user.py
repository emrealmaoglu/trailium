#!/usr/bin/env python3
"""
🎯 Trailium Custom User Creation Script
Bu script, kullanıcıdan bilgi alarak veya JSON dosyasından okuyarak özel kullanıcı oluşturur.
"""

import json
import os
import sys
import subprocess
from pathlib import Path

def load_user_from_json(json_file_path):
    """JSON dosyasından kullanıcı bilgilerini yükle"""
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # JSON formatını script formatına dönüştür
        user_data = {
            'profile': {
                'first_name': data['user']['fields']['first_name'],
                'last_name': data['user']['fields']['last_name'],
                'username': data['user']['fields']['username'],
                'email': data['user']['fields']['email'],
                'phone': data['user']['fields']['phone'],
                'city': data['user']['fields']['city'],
                'company': data['user']['fields']['company'],
                'bio': data['user']['fields']['bio'],
                'gender': data['user']['fields']['gender'],
                'is_premium': data['user']['fields']['is_premium'],
                'is_private': data['user']['fields']['is_private']
            },
            'posts': [
                {
                    'title': post['title'],
                    'body': post['body']
                } for post in data['posts']
            ],
            'todos': [
                {
                    'title': todo['title'],
                    'items': [
                        {
                            'task': item['task'],
                            'description': item['description'],
                            'subtasks': item['subtasks']
                        } for item in todo['items']
                    ]
                } for todo in data['todos']
            ],
            'albums': [
                {
                    'title': album['title'],
                    'photos': album['photos']
                } for album in data['albums']
            ]
        }

        return user_data
    except Exception as e:
        print(f"❌ JSON dosyası okunamadı: {e}")
        return None

def create_user_from_json(json_file_path):
    """JSON dosyasından kullanıcı oluştur"""
    print(f"📁 JSON dosyası okunuyor: {json_file_path}")

    user_data = load_user_from_json(json_file_path)
    if not user_data:
        return False

    print("✅ JSON verisi başarıyla yüklendi!")
    print(f"👤 Kullanıcı: {user_data['profile']['first_name']} {user_data['profile']['last_name']}")
    print(f"📝 Post sayısı: {len(user_data['posts'])}")
    print(f"✅ Todo listesi sayısı: {len(user_data['todos'])}")
    print(f"📸 Albüm sayısı: {len(user_data['albums'])}")

    # Django management command'ını çağır
    return call_django_command(user_data)

def call_django_command(user_data):
    """Django management command'ını çağır"""
    try:
        # Django projesi dizinine git
        backend_dir = Path(__file__).parent / "apps" / "backend"
        if not backend_dir.exists():
            print("❌ Backend dizini bulunamadı!")
            return False

        # Kullanıcı verisini JSON olarak hazırla
        command_data = {
            'profile': user_data['profile'],
            'posts': user_data['posts'],
            'todos': user_data['todos'],
            'albums': user_data['albums']
        }

        # Django command'ını çalıştır
        cmd = [
            'python', 'manage.py', 'create_custom_user',
            '--data', json.dumps(command_data, ensure_ascii=False)
        ]

        print("🚀 Django command çalıştırılıyor...")
        result = subprocess.run(cmd, cwd=backend_dir, capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Kullanıcı başarıyla oluşturuldu!")
            print(result.stdout)
            return True
        else:
            print("❌ Kullanıcı oluşturulamadı!")
            print(result.stderr)
            return False

    except Exception as e:
        print(f"❌ Hata: {e}")
        return False

def main():
    """Ana fonksiyon"""
    print("🎯 Trailium Custom User Creation Script")
    print("=" * 50)

    if len(sys.argv) > 1:
        # Komut satırından JSON dosyası belirtilmiş
        json_file = sys.argv[1]
        if not os.path.exists(json_file):
            print(f"❌ Dosya bulunamadı: {json_file}")
            return

        create_user_from_json(json_file)
    else:
        # İnteraktif mod
        print("📋 Kullanım seçenekleri:")
        print("1. JSON dosyasından kullanıcı oluştur")
        print("2. İnteraktif olarak kullanıcı oluştur")
        print("3. Çıkış")

        choice = input("\nSeçiminiz (1-3): ").strip()

        if choice == "1":
            json_file = input("JSON dosya yolu: ").strip()
            if os.path.exists(json_file):
                create_user_from_json(json_file)
            else:
                print(f"❌ Dosya bulunamadı: {json_file}")
        elif choice == "2":
            # Mevcut interaktif fonksiyonu çağır
            # This part of the original script was removed as per the new_code.
            # The new_code only provided the JSON-based flow.
            # If the user wants to re-introduce the interactive mode,
            # they need to provide the full interactive logic here.
            print("Interactive mode is not fully implemented in the new_code.")
            print("Please run the script with a JSON file or provide all inputs manually.")
        elif choice == "3":
            print("👋 Görüşürüz!")
        else:
            print("❌ Geçersiz seçim!")

if __name__ == "__main__":
    main()
