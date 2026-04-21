<template>
  <div class="ai-settings">
    <el-card>
      <template #header>
        <span>AI 模型配置</span>
      </template>
      
      <el-tabs v-model="activeTab">
        <!-- LLM 对话模型 -->
        <el-tab-pane label="对话模型 (LLM)" name="llm">
          <el-form :model="llmConfig" label-width="120px">
            <el-form-item label="模型服务">
              <el-select v-model="llmConfig.provider" @change="onProviderChange">
                <el-option label="通义千问" value="dashscope" />
                <el-option label="OpenAI" value="openai" />
                <el-option label="DeepSeek" value="deepseek" />
                <el-option label="Moonshot" value="moonshot" />
                <el-option label="自定义 (OpenAI 兼容)" value="custom" />
                <el-option label="本地模型 (Ollama)" value="local" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="Base URL" v-if="showBaseUrl">
              <el-input v-model="llmConfig.base_url" placeholder="https://api.xxx.com" />
            </el-form-item>
            
            <el-form-item label="API Key">
              <el-input v-model="llmConfig.api_key" type="password" show-password />
            </el-form-item>
            
            <el-form-item label="模型名称">
              <el-input v-model="llmConfig.model_name" placeholder="qwen-max" />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="testConnection('llm')" :loading="testing">
                测试连接
              </el-button>
              <el-button type="success" @click="saveConfig('llm')" :loading="saving">
                保存配置
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <!-- 向量化模型 -->
        <el-tab-pane label="向量化模型 (Embedding)" name="embedding">
          <el-form :model="embeddingConfig" label-width="120px">
            <el-form-item label="模型服务">
              <el-select v-model="embeddingConfig.provider">
                <el-option label="通义千问" value="dashscope" />
                <el-option label="OpenAI" value="openai" />
                <el-option label="自定义 (OpenAI 兼容)" value="custom" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="Base URL" v-if="showEmbeddingBaseUrl">
              <el-input v-model="embeddingConfig.base_url" placeholder="https://api.xxx.com" />
            </el-form-item>
            
            <el-form-item label="API Key">
              <el-input v-model="embeddingConfig.api_key" type="password" />
            </el-form-item>
            
            <el-form-item label="模型名称">
              <el-input v-model="embeddingConfig.model_name" placeholder="text-embedding-v2" />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="testConnection('embedding')" :loading="testing">
                测试连接
              </el-button>
              <el-button type="success" @click="saveConfig('embedding')" :loading="saving">
                保存配置
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
    
    <el-alert
      title="配置说明"
      type="info"
      :closable="false"
      style="margin-top: 20px"
    >
      <p>1. 对话模型用于简历评分和面试题目生成</p>
      <p>2. 向量化模型用于人才库相似度搜索（可选配置）</p>
      <p>3. 通义千问无需配置 Base URL，其他服务需要填写对应 API 地址</p>
    </el-alert>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { aiApi } from '@/api'

const activeTab = ref('llm')
const testing = ref(false)
const saving = ref(false)

const llmConfig = ref({
  name: '默认对话模型',
  provider: 'dashscope',
  base_url: '',
  api_key: '',
  model_name: 'qwen-max',
  model_type: 'llm',
  extra_config: {}
})

const embeddingConfig = ref({
  name: '默认向量化模型',
  provider: 'dashscope',
  base_url: '',
  api_key: '',
  model_name: 'text-embedding-v2',
  model_type: 'embedding',
  extra_config: {}
})

const showBaseUrl = computed(() => {
  return ['openai', 'custom', 'local'].includes(llmConfig.value.provider)
})

const showEmbeddingBaseUrl = computed(() => {
  return ['openai', 'custom'].includes(embeddingConfig.value.provider)
})

const onProviderChange = () => {
  // 预设常用服务的 API 地址
  const providerUrls = {
    'openai': 'https://api.openai.com/v1',
    'deepseek': 'https://api.deepseek.com/v1',
    'moonshot': 'https://api.moonshot.cn/v1',
    'custom': '',
    'local': 'http://localhost:11434'
  }
  llmConfig.value.base_url = providerUrls[llmConfig.value.provider] || ''
}

const loadConfigs = async () => {
  try {
    const res = await aiApi.listModels()
    const configs = res.data || []
    const llm = configs.find((c: any) => c.model_type === 'llm')
    const embedding = configs.find((c: any) => c.model_type === 'embedding')
    
    if (llm) {
      llmConfig.value = { ...llmConfig.value, ...llm }
    }
    if (embedding) {
      embeddingConfig.value = { ...embeddingConfig.value, ...embedding }
    }
  } catch (e) {
    console.error('加载配置失败', e)
  }
}

const testConnection = async (type: string) => {
  const config = type === 'llm' ? llmConfig.value : embeddingConfig.value
  if (!config.api_key) {
    ElMessage.warning('请先填写 API Key')
    return
  }
  
  testing.value = true
  try {
    // 先保存再测试
    let configId = config.id
    if (!configId) {
      const res = await aiApi.createModel(config)
      configId = res.data.id
    }
    
    const res = await aiApi.testModel(configId)
    if (res.data.success) {
      ElMessage.success(res.data.message)
    } else {
      ElMessage.error(res.data.message)
    }
  } catch (e) {
    ElMessage.error('测试失败：' + (e as any).response?.data?.message || '未知错误')
  } finally {
    testing.value = false
  }
}

const saveConfig = async (type: string) => {
  const config = type === 'llm' ? llmConfig.value : embeddingConfig.value
  if (!config.api_key) {
    ElMessage.warning('请填写 API Key')
    return
  }
  
  saving.value = true
  try {
    if (config.id) {
      await aiApi.updateModel(config.id, config)
    } else {
      config.is_default = true
      config.is_active = true
      await aiApi.createModel(config)
    }
    ElMessage.success('保存成功')
    loadConfigs()
  } catch (e) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadConfigs()
})
</script>

<style scoped>
.ai-settings {
  max-width: 800px;
  margin: 0 auto;
}
</style>
