<template>
  <div id="app">
    <div class="app-container">
      <!-- 侧边栏 -->
      <aside class="sidebar">
        <div class="sidebar-header">
          <h1 class="logo-text">HR·AI</h1>
          <p class="logo-subtitle">招聘管理系统</p>
        </div>

        <nav class="sidebar-nav">
          <router-link to="/" class="nav-item" :class="{ active: $route.path === '/' }">
            <HomeFilled class="nav-icon" />
            <span class="nav-label">岗位管理</span>
          </router-link>

          <router-link to="/talent-pool" class="nav-item" :class="{ active: $route.path === '/talent-pool' }">
            <User class="nav-icon" />
            <span class="nav-label">人才库</span>
          </router-link>

          <router-link to="/ai-settings" class="nav-item" :class="{ active: $route.path === '/ai-settings' }">
            <Setting class="nav-icon" />
            <span class="nav-label">AI 配置</span>
          </router-link>
        </nav>

        <div class="sidebar-footer">
          <p class="footer-text">企业级招聘解决方案</p>
        </div>
      </aside>

      <!-- 主内容区 -->
      <main class="main-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { HomeFilled, User, Setting } from '@element-plus/icons-vue'
</script>

<style>
@import './styles/tokens.css';

body, html {
  margin: 0;
  padding: 0;
  height: 100%;
}

#app {
  height: 100%;
}

.app-container {
  display: flex;
  height: 100%;
  background-color: var(--color-bg);
}

/* 侧边栏样式 */
.sidebar {
  width: 280px;
  background: linear-gradient(180deg, var(--color-brand-dark) 0%, var(--color-brand) 100%);
  display: flex;
  flex-direction: column;
  border-right: 1px solid var(--color-border);
}

.sidebar-header {
  padding: var(--space-8) var(--space-6);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo-text {
  font-family: var(--font-display);
  font-size: var(--text-3xl);
  font-weight: var(--font-bold);
  color: white;
  margin: 0;
  letter-spacing: 0.05em;
}

.logo-subtitle {
  font-size: var(--text-sm);
  color: rgba(255, 255, 255, 0.7);
  margin: var(--space-2) 0 0 0;
  font-weight: var(--font-normal);
}

.sidebar-nav {
  flex: 1;
  padding: var(--space-4) 0;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: var(--space-4) var(--space-6);
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  transition: all var(--duration-fast) var(--ease-out);
  border-left: 3px solid transparent;
  gap: var(--space-3);
}

.nav-item:hover {
  background-color: rgba(255, 255, 255, 0.08);
  color: white;
}

.nav-item.active {
  background-color: rgba(255, 255, 255, 0.12);
  color: white;
  border-left-color: var(--color-accent);
}

.nav-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.nav-label {
  font-size: var(--text-base);
  font-weight: var(--font-medium);
}

.sidebar-footer {
  padding: var(--space-6);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.footer-text {
  font-size: var(--text-xs);
  color: rgba(255, 255, 255, 0.5);
  margin: 0;
  text-align: center;
}

/* 主内容区样式 */
.main-content {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-8);
}

/* 响应式 */
@media (max-width: 768px) {
  .sidebar {
    width: 220px;
  }

  .main-content {
    padding: var(--space-4);
  }
}
</style>
