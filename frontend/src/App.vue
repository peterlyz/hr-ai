<template>
  <div id="app">
    <el-container>
      <el-aside width="220px">
        <div class="logo">
          <h2>招聘智能助手</h2>
        </div>
        <el-menu
          :default-active="$route.path"
          router
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409EFF"
        >
          <el-menu-item index="/">
            <el-icon><HomeFilled /></el-icon>
            <span>首页</span>
          </el-menu-item>
          <el-menu-item index="/talent-pool">
            <el-icon><User /></el-icon>
            <span>人才库</span>
          </el-menu-item>
          <el-menu-item index="/ai-settings">
            <el-icon><Setting /></el-icon>
            <span>AI 配置</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { HomeFilled, User, Setting } from '@element-plus/icons-vue'
</script>

<style>
body, html {
  margin: 0;
  padding: 0;
  height: 100%;
}

#app {
  height: 100%;
}

.el-container {
  height: 100%;
}

.el-aside {
  background-color: #304156;
  color: #fff;
}

.logo {
  padding: 20px;
  text-align: center;
  background-color: #2b3a4b;
}

.logo h2 {
  color: #fff;
  font-size: 18px;
  margin: 0;
}

.el-menu {
  border-right: none;
}

.el-main {
  background-color: #f0f2f5;
  padding: 20px;
}
</style>
