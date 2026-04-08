<script setup lang="ts">
import type { NavigationMenuItem } from '@nuxt/ui'

const { user, isAdmin, logout } = useAuth()
const sidebarOpen = ref(true)
const mobileSidebarOpen = ref(false)

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
  <div class="flex h-screen overflow-hidden bg-default">
    <!-- Mobile sidebar overlay -->
    <div
      v-if="mobileSidebarOpen"
      class="fixed inset-0 z-40 bg-black/50 lg:hidden"
      @click="mobileSidebarOpen = false"
    />

    <!-- Sidebar -->
    <aside
      class="fixed inset-y-0 left-0 z-50 flex flex-col border-r border-default bg-elevated transition-all duration-200 lg:relative lg:z-auto"
      :class="[
        mobileSidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0',
        sidebarOpen ? 'w-64' : 'w-16',
      ]"
    >
      <!-- Header -->
      <div class="flex items-center gap-2 p-3 border-b border-default">
        <NuxtLink to="/archive" class="flex items-center gap-2 min-w-0">
          <img src="~/assets/images/logos/logo-no-text.svg" class="h-8 w-8 shrink-0" alt="Logo" />
          <span v-if="sidebarOpen" class="font-bold text-sm text-highlighted truncate">
            Arxiv tizimi
          </span>
        </NuxtLink>
        <UButton
          v-if="sidebarOpen"
          icon="i-lucide-panel-left-close"
          variant="ghost"
          size="xs"
          class="ml-auto hidden lg:flex"
          @click="sidebarOpen = false"
        />
      </div>

      <!-- Collapse toggle (when collapsed) -->
      <div v-if="!sidebarOpen" class="hidden lg:flex justify-center py-2">
        <UButton
          icon="i-lucide-panel-left-open"
          variant="ghost"
          size="xs"
          @click="sidebarOpen = true"
        />
      </div>

      <!-- Navigation -->
      <nav class="flex-1 overflow-y-auto p-2">
        <UNavigationMenu
          :items="navItems"
          orientation="vertical"
          :ui="{ link: !sidebarOpen ? 'justify-center' : undefined }"
        />
      </nav>

      <!-- Footer - user menu -->
      <div class="border-t border-default p-2">
        <UDropdownMenu :items="userMenuItems">
          <UButton variant="ghost" block :class="sidebarOpen ? 'justify-start' : 'justify-center'">
            <UAvatar :text="user?.name?.charAt(0)" size="xs" />
            <span v-if="sidebarOpen" class="truncate text-sm">{{ user?.name }}</span>
          </UButton>
        </UDropdownMenu>
      </div>
    </aside>

    <!-- Main content -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <!-- Top bar (mobile) -->
      <div class="flex items-center gap-2 p-2 border-b border-default lg:hidden">
        <UButton
          icon="i-lucide-menu"
          variant="ghost"
          @click="mobileSidebarOpen = !mobileSidebarOpen"
        />
        <span class="font-bold text-sm text-highlighted">Arxiv tizimi</span>
      </div>

      <!-- Page content -->
      <main class="flex-1 overflow-y-auto">
        <slot />
      </main>
    </div>
  </div>
</template>
