import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import UserCard from '../UserCard.vue'

// Mock the router
const mockRouter = {
  push: vi.fn()
}

// Mock the http module
vi.mock('@/lib/http', () => ({
  json: vi.fn()
}))

// Mock vue-router
vi.mock('vue-router', () => ({
  useRouter: () => mockRouter
}))

describe('UserCard', () => {
  let wrapper
  const mockUser = {
    id: 1,
    name: 'John Doe',
    email: 'john@example.com',
    phone: '+1234567890',
    addressText: '123 Main St, City',
    companyName: 'Tech Corp',
    website: 'https://techcorp.com',
    is_premium: false,
    is_private: false,
    avatar: '',
    about: 'Software developer',
    created_at: '2025-01-01T00:00:00Z'
  }

  beforeEach(() => {
    wrapper = mount(UserCard, {
      props: { user: mockUser },
      global: {
        mocks: {
          $router: mockRouter
        }
      }
    })
  })

  it('renders user information correctly', () => {
    expect(wrapper.find('.user-name').text()).toBe('John Doe')
    expect(wrapper.find('.user-email').text()).toBe('john@example.com')
    expect(wrapper.find('.user-phone').text()).toBe('+1234567890')
  })

  it('displays user initials in avatar', () => {
    const avatar = wrapper.find('.avatar-placeholder')
    expect(avatar.text()).toBe('J')
  })

  it('shows premium badge for premium users', async () => {
    await wrapper.setProps({
      user: { ...mockUser, is_premium: true }
    })

    const premiumBadge = wrapper.find('.premium-badge')
    expect(premiumBadge.exists()).toBe(true)
    expect(premiumBadge.text()).toBe('⭐')
  })

  it('shows private indicator for private accounts', async () => {
    await wrapper.setProps({
      user: { ...mockUser, is_private: true }
    })

    const privateIndicator = wrapper.find('.private-indicator')
    expect(privateIndicator.exists()).toBe(true)
    expect(privateIndicator.text()).toBe('🔒')
  })

  it('shows new user badge for recently created users', async () => {
    const recentUser = {
      ...mockUser,
      created_at: new Date().toISOString()
    }

    await wrapper.setProps({ user: recentUser })

    const newUserBadge = wrapper.find('.new-user-badge')
    expect(newUserBadge.exists()).toBe(true)
    expect(newUserBadge.text()).toBe('🆕')
  })

  it('displays contact information when available', () => {
    const addressItem = wrapper.find('.detail-item')
    expect(addressItem.exists()).toBe(true)
    expect(addressItem.text()).toContain('123 Main St, City')
  })

  it('shows about section when available', () => {
    const aboutSection = wrapper.find('.user-about')
    expect(aboutSection.exists()).toBe(true)
    expect(aboutSection.text()).toContain('Software developer')
  })

  it('displays member since date', () => {
    const memberSince = wrapper.find('.stat-value')
    expect(memberSince.exists()).toBe(true)
    expect(memberSince.text()).toContain('1/1/2025')
  })

  it('navigates to user todos when clicked', async () => {
    await wrapper.trigger('click')

    expect(mockRouter.push).toHaveBeenCalledWith('/users/1/todos')
  })

  it('handles keyboard navigation', async () => {
    await wrapper.trigger('keydown.enter')
    expect(mockRouter.push).toHaveBeenCalledWith('/users/1/todos')

    await wrapper.trigger('keydown.space')
    expect(mockRouter.push).toHaveBeenCalledWith('/users/1/todos')
  })

  it('renders follow button with correct text', () => {
    const followBtn = wrapper.find('.follow-btn')
    expect(followBtn.exists()).toBe(true)
    expect(followBtn.text()).toContain('Takip Et')
  })

  it('handles missing user data gracefully', async () => {
    const minimalUser = {
      id: 1,
      name: 'Minimal User'
    }

    await wrapper.setProps({ user: minimalUser })

    expect(wrapper.find('.user-email').text()).toBe('No email')
    expect(wrapper.find('.user-phone').text()).toBe('No phone')
  })

  it('applies correct CSS classes based on user status', async () => {
    // Test premium user
    await wrapper.setProps({
      user: { ...mockUser, is_premium: true }
    })

    expect(wrapper.find('.premium-badge').exists()).toBe(true)

    // Test private user
    await wrapper.setProps({
      user: { ...mockUser, is_private: true }
    })

    expect(wrapper.find('.private-indicator').exists()).toBe(true)
  })

  it('has proper accessibility attributes', () => {
    const card = wrapper.find('.user-card')
    expect(card.attributes('role')).toBe('button')
    expect(card.attributes('tabindex')).toBe('0')
  })

  it('handles empty about text gracefully', async () => {
    await wrapper.setProps({
      user: { ...mockUser, about: '' }
    })

    const aboutSection = wrapper.find('.user-about')
    expect(aboutSection.exists()).toBe(false)
  })

  it('handles missing created_at gracefully', async () => {
    await wrapper.setProps({
      user: { ...mockUser, created_at: null }
    })

    const memberSince = wrapper.find('.stat-value')
    expect(memberSince.text()).toBe('Unknown')
  })
})
