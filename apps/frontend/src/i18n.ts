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
      usersWord: 'kullanıcı',
      empty: 'Henüz kullanıcı bulunamadı',
      error: 'Kullanıcılar yüklenemedi',
      retry: 'Tekrar dene',
      pagination: { prev: 'Önceki', next: 'Sonraki' }
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
    },
    user: {
      notFound: 'Kullanıcı bulunamadı',
      comingSoon: 'Yakında',
      tabs: { todos: 'Yapılacaklar', posts: 'Gönderiler', albums: 'Albümler' }
    },
    posts: {
      title: 'Gönderiler',
      addPost: 'Gönderi ekle',
      empty: 'Henüz gönderi yok',
      error: 'Bir hata oluştu',
      like: 'Beğen',
      unlike: 'Beğeniyi geri al',
      seeMore: 'Devamını gör',
      comments: 'Yorumlar',
      addComment: 'Yorum ekle',
      comment: 'Yorum Yap'
    },
    albums: {
      title: 'Albümler',
      addAlbum: 'Albüm ekle',
      empty: 'Henüz albüm yok',
      error: 'Bir hata oluştu',
      photos: 'fotoğraf'
    },
    photos: {
      addPhoto: 'Fotoğraf ekle'
    },
    settings: {
      title: 'Ayarlar',
      name: 'Ad Soyad',
      email: 'E-posta',
      password: 'Şifre (demo)',
      visibility: 'Görünürlük',
      private: 'Gizli hesap',
      premium: 'Premium',
      save: 'Kaydet',
      success: 'Kaydedildi',
      error: 'Hata oluştu'
    },
    todos: {
      title: 'Yapılacaklar',
      addList: 'Liste ekle',
      addItem: 'Öğe ekle',
      addSubItem: 'Alt öğe ekle',
      delete: 'Sil',
      edit: 'Düzenle',
      save: 'Kaydet',
      cancel: 'İptal',
      emptyLists: 'Henüz liste yok',
      emptyItems: 'Bu listede öğe yok',
      error: 'Bir hata oluştu',
      retry: 'Tekrar dene',
      progress: 'İlerleme',
      items: 'Öğeler',
      subitems: 'Alt öğeler',
      due: 'Son tarih',
      kind: { daily: 'Günlük', work: 'İş', home: 'Ev', personal: 'Kişisel', other: 'Diğer' },
      pagination: { prev: 'Önceki', next: 'Sonraki' }
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
      usersWord: 'users',
      empty: 'No users yet',
      error: 'Failed to load users',
      retry: 'Retry',
      pagination: { prev: 'Previous', next: 'Next' }
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
    },
    user: {
      notFound: 'User not found',
      comingSoon: 'Coming soon',
      tabs: { todos: 'Todos', posts: 'Posts', albums: 'Albums' }
    },
    posts: {
      title: 'Posts',
      addPost: 'Add post',
      empty: 'No posts yet',
      error: 'Something went wrong',
      like: 'Like',
      unlike: 'Unlike',
      seeMore: 'See more',
      comments: 'Comments',
      addComment: 'Add a comment',
      comment: 'Comment'
    },
    albums: {
      title: 'Albums',
      addAlbum: 'Add album',
      empty: 'No albums yet',
      error: 'Something went wrong',
      photos: 'photos'
    },
    photos: {
      addPhoto: 'Add photo'
    },
    settings: {
      title: 'Settings',
      name: 'Full name',
      email: 'Email',
      password: 'Password (demo)',
      visibility: 'Visibility',
      private: 'Private account',
      premium: 'Premium',
      save: 'Save',
      success: 'Saved',
      error: 'Error occurred'
    },
    todos: {
      title: 'Todos',
      addList: 'Add list',
      addItem: 'Add item',
      addSubItem: 'Add sub-item',
      delete: 'Delete',
      edit: 'Edit',
      save: 'Save',
      cancel: 'Cancel',
      emptyLists: 'No lists yet',
      emptyItems: 'No items in this list',
      error: 'Something went wrong',
      retry: 'Retry',
      progress: 'Progress',
      items: 'Items',
      subitems: 'Sub-items',
      due: 'Due',
      kind: { daily: 'Daily', work: 'Work', home: 'Home', personal: 'Personal', other: 'Other' },
      pagination: { prev: 'Previous', next: 'Next' }
    }
  }
}

const saved = typeof window !== 'undefined' ? (localStorage.getItem('lang') || 'tr') : 'tr'

const i18n = createI18n({
  legacy: false,
  locale: saved,
  fallbackLocale: 'en',
  messages
})

export function setLocale(lang: 'tr' | 'en') {
  i18n.global.locale.value = lang
  try { localStorage.setItem('lang', lang) } catch {}
}

export default i18n

