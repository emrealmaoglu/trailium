import { createI18n } from 'vue-i18n'

const messages = {
  tr: {
    auth: {
      login: 'Giriş Yap',
      register: 'Kayıt Ol',
      username: 'Kullanıcı adı',
      email: 'E-posta',
      password: 'Şifre',
      rememberMe: 'Beni hatırla',
      signInCta: 'Giriş Yap',
      createAccountCta: 'Hesap Oluştur',
      haveNoAccount: 'Hesabın yok mu?',
      haveAccount: 'Zaten hesabın var mı?',
      welcomeBack: 'Tekrar hoş geldin! Lütfen giriş yap.',
      loginFailed: 'Giriş başarısız. Lütfen bilgilerinizi kontrol edin.'
    },
    users: {
      title: 'Kullanıcılar',
      filters: 'Filtreler',
      searchPlaceholder: 'Kullanıcı ara...',
      premiumOnly: '⭐ Sadece premium',
      privateOnly: '🔒 Sadece gizli hesaplar',
      clearFilters: 'Filtreleri Temizle',
      loading: 'Kullanıcılar yükleniyor...',
      emptyTitle: 'Kullanıcı bulunamadı',
      emptyHint: 'Henüz kullanıcı yok',
      showing: 'Gösterilen',
      of: 'toplam',
      usersWord: 'kullanıcı'
    },
    menu: {
      profile: 'Profil',
      settings: 'Ayarlar',
      logout: 'Çıkış',
      theme: 'Tema',
      light: 'Açık',
      dark: 'Koyu',
      system: 'Sistem',
      language: 'Dil',
      turkish: 'Türkçe',
      english: 'İngilizce'
    }
  },
  en: {
    auth: {
      login: 'Sign In',
      register: 'Sign Up',
      username: 'Username',
      email: 'Email',
      password: 'Password',
      rememberMe: 'Remember me',
      signInCta: 'Sign In',
      createAccountCta: 'Create account',
      haveNoAccount: "Don't have an account?",
      haveAccount: 'Already have an account?',
      welcomeBack: 'Welcome back! Please sign in to your account.',
      loginFailed: 'Login failed. Please check your credentials.'
    },
    users: {
      title: 'All Users',
      filters: 'Filters',
      searchPlaceholder: 'Search users...',
      premiumOnly: '⭐ Premium users only',
      privateOnly: '🔒 Private accounts only',
      clearFilters: 'Clear Filters',
      loading: 'Loading users...',
      emptyTitle: 'No users found',
      emptyHint: 'No users available yet',
      showing: 'Showing',
      of: 'of',
      usersWord: 'users'
    },
    menu: {
      profile: 'Profile',
      settings: 'Settings',
      logout: 'Logout',
      theme: 'Theme',
      light: 'Light',
      dark: 'Dark',
      system: 'System',
      language: 'Language',
      turkish: 'Turkish',
      english: 'English'
    }
  }
}

const saved = typeof window !== 'undefined' ? (localStorage.getItem('lang') || 'tr') : 'tr'

export const i18n = createI18n({
  legacy: false,
  locale: saved,
  fallbackLocale: 'en',
  messages
})

export function setLocale(lang: 'tr' | 'en') {
  i18n.global.locale.value = lang
  try { localStorage.setItem('lang', lang) } catch {}
}


