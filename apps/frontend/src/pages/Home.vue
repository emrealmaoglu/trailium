<template>
  <section>
    <div style="margin-bottom: 32px;">
      <h1 style="font-size: 32px; font-weight: 700; margin-bottom: 12px; color: var(--c-text);">
        Welcome to Trailium 👋
      </h1>
      <p style="font-size: 18px; color: var(--c-text-muted); line-height: 1.6;">
        Your comprehensive social platform for managing users, todos, posts, and albums.
      </p>
    </div>

    <div class="grid grid-cols-responsive" style="gap: 24px;">
      <div class="card" style="padding: 24px; cursor: pointer;" @click="$router.push('/users')">
        <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 16px;">
          <div style="width: 48px; height: 48px; background: linear-gradient(135deg, #ff4db0, #4db2ff); border-radius: 12px; display: grid; place-items: center; color: white; font-size: 24px;">
            👥
          </div>
          <div>
            <h3 style="font-size: 20px; font-weight: 600; margin: 0; color: var(--c-text);">Users</h3>
            <p style="margin: 4px 0 0; color: var(--c-text-muted);">Browse and connect with users</p>
          </div>
        </div>
        <p style="color: var(--c-text-muted); line-height: 1.5;">
          Discover users, view profiles, and manage your connections. Follow users to see their content in your feed.
        </p>
      </div>

      <div class="card" style="padding: 24px; cursor: pointer;" @click="$router.push('/todos')">
        <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 16px;">
          <div style="width: 48px; height: 48px; background: linear-gradient(135deg, #4db2ff, #4dffb2); border-radius: 12px; display: grid; place-items: center; color: white; font-size: 24px;">
            ✅
          </div>
          <div>
            <h3 style="font-size: 20px; font-weight: 600; margin: 0; color: var(--c-text);">Todos</h3>
            <p style="margin: 4px 0 0; color: var(--c-text-muted);">Manage your tasks and lists</p>
          </div>
        </div>
        <p style="color: var(--c-text-muted); line-height: 1.5;">
          Create and organize your todo lists with progress tracking. Break down tasks into subtasks for better organization.
        </p>
      </div>

      <div class="card" style="padding: 24px; cursor: pointer;" @click="$router.push('/posts')">
        <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 16px;">
          <div style="width: 48px; height: 48px; background: linear-gradient(135deg, #4dffb2, #b24dff); border-radius: 12px; display: grid; place-items: center; color: white; font-size: 24px;">
            📝
          </div>
          <div>
            <h3 style="font-size: 20px; font-weight: 600; margin: 0; color: var(--c-text);">Posts</h3>
            <p style="margin: 4px 0 0; color: var(--c-text-muted);">Share and discover content</p>
          </div>
        </div>
        <p style="color: var(--c-text-muted); line-height: 1.5;">
          Read posts from users, like and comment on content. Share your thoughts and engage with the community.
        </p>
      </div>

      <div class="card" style="padding: 24px; cursor: pointer;" @click="$router.push('/albums')">
        <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 16px;">
          <div style="width: 48px; height: 48px; background: linear-gradient(135deg, #b24dff, #ff4db0); border-radius: 12px; display: grid; place-items: center; color: white; font-size: 24px;">
            📸
          </div>
          <div>
            <h3 style="font-size: 20px; font-weight: 600; margin: 0; color: var(--c-text);">Albums</h3>
            <p style="margin: 4px 0 0; color: var(--c-text-muted);">Organize your photos</p>
          </div>
        </div>
        <p style="color: var(--c-text-muted); line-height: 1.5;">
          Create photo albums and organize your memories. Share visual content with your followers.
        </p>
      </div>

      <div class="card" style="padding: 24px; cursor: pointer;" @click="$router.push('/feed')">
        <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 16px;">
          <div style="width: 48px; height: 48px; background: linear-gradient(135deg, #ff4db0, #ffb24d); border-radius: 12px; display: grid; place-items: center; color: white; font-size: 24px;">
            🔄
          </div>
          <div>
            <h3 style="font-size: 20px; font-weight: 600; margin: 0; color: var(--c-text);">Feed</h3>
            <p style="margin: 4px 0 0; color: var(--c-text-muted);">Your personalized content stream</p>
          </div>
        </div>
        <p style="color: var(--c-text-muted); line-height: 1.5;">
          View posts from users you follow in a personalized feed. Stay updated with content that matters to you.
        </p>
      </div>

      <div class="card" style="padding: 24px; cursor: pointer;" @click="$router.push('/settings')">
        <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 16px;">
          <div style="width: 48px; height: 48px; background: linear-gradient(135deg, #ffb24d, #4db2ff); border-radius: 12px; display: grid; place-items: center; color: white; font-size: 24px;">
            ⚙️
          </div>
          <div>
            <h3 style="font-size: 20px; font-weight: 600; margin: 0; color: var(--c-text);">Settings</h3>
            <p style="margin: 4px 0 0; color: var(--c-text-muted);">Manage your account</p>
          </div>
        </div>
        <p style="color: var(--c-text-muted); line-height: 1.5;">
          Update your profile, change password, and manage your account settings. Control your privacy and preferences.
        </p>
      </div>
    </div>
  </section>
</template>
