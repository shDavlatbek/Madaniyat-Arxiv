<script setup lang="ts">
import type { NavigationMenuItem } from '@nuxt/ui'

const { user, isAdmin, logout } = useAuth()

const navItems = computed<NavigationMenuItem[]>(() => {
  const items: NavigationMenuItem[] = [
    { label: 'Arxiv', icon: 'i-lucide-archive', to: '/archive' },
  ]
  if (isAdmin.value) {
    items.push(
      { label: 'Yillar', icon: 'i-lucide-calendar', to: '/admin/years' },
      { label: 'Kategoriyalar', icon: 'i-lucide-folder', to: '/admin/categories' },
      { label: 'Foydalanuvchilar', icon: 'i-lucide-users', to: '/admin/users' },
    )
  }
  return items
})

const userMenuItems = computed(() => [
  [
    { label: user.value?.name || '', type: 'label' as const },
    { label: user.value?.role || '', type: 'label' as const },
  ],
  [
    { label: 'Chiqish', icon: 'i-lucide-log-out', onSelect: logout },
  ],
])
</script>

<template>
  <UDashboardGroup>
    <UDashboardSidebar collapsible resizable>
      <template #header="{ collapsed }">
        <NuxtLink to="/archive" class="flex items-center gap-2 p-2">
          <img src="~/assets/images/logos/logo-no-text.svg" class="h-8 w-8 shrink-0" alt="Logo" />
          <span v-if="!collapsed" class="font-bold text-sm text-highlighted truncate">
            Arxiv tizimi
          </span>
        </NuxtLink>
      </template>

      <template #default="{ collapsed }">
        <UNavigationMenu
          :items="navItems"
          orientation="vertical"
          :ui="{ link: collapsed ? 'justify-center' : undefined }"
        />
      </template>

      <template #footer="{ collapsed }">
        <UDropdownMenu :items="userMenuItems">
          <UButton variant="ghost" block class="justify-start">
            <UAvatar :text="user?.name?.charAt(0)" size="xs" />
            <span v-if="!collapsed" class="truncate text-sm">{{ user?.name }}</span>
          </UButton>
        </UDropdownMenu>
      </template>
    </UDashboardSidebar>

    <slot />
  </UDashboardGroup>
</template>
