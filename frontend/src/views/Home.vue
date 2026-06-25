<template>
  <div class="home-page">
    <!-- 页面头部 -->
    <header class="page-header">
      <div class="header-content">
        <div>
          <h1 class="page-title">岗位管理</h1>
          <p class="page-subtitle">创建岗位、导入简历、筛选候选人</p>
        </div>
        <button class="btn-primary" @click="showCreateDialog = true">
          <Plus class="btn-icon" />
          新建岗位
        </button>
      </div>
    </header>

    <!-- 岗位列表 -->
    <div class="jobs-container">
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>加载中...</p>
      </div>

      <div v-else-if="jobs.length === 0" class="empty-state">
        <p class="empty-title">暂无岗位</p>
        <p class="empty-text">点击"新建岗位"开始招聘流程</p>
      </div>

      <div v-else class="jobs-grid">
        <div
          v-for="job in jobs"
          :key="job.id"
          class="job-card"
          @click="$router.push(`/job/${job.id}`)"
        >
          <div class="job-card-header">
            <h3 class="job-title">{{ job.title }}</h3>
            <span class="job-status" :class="job.status">
              {{ job.status === 'active' ? '招聘中' : '已关闭' }}
            </span>
          </div>

          <div class="job-meta">
            <span v-if="job.department" class="meta-item">
              <span class="meta-label">部门：</span>
              <span class="meta-value">{{ job.department }}</span>
            </span>
            <span class="meta-item">
              <span class="meta-label">创建时间：</span>
              <span class="meta-value">{{ formatDate(job.created_at) }}</span>
            </span>
          </div>

          <div class="job-actions" @click.stop>
            <button class="btn-secondary btn-sm" @click="$router.push(`/job/${job.id}`)">
              查看详情
            </button>
            <button class="btn-danger btn-sm" @click="handleDelete(job.id)">
              删除
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 创建岗位对话框 -->
    <div v-if="showCreateDialog" class="modal-overlay" @click="showCreateDialog = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2 class="modal-title">新建岗位</h2>
          <button class="modal-close" @click="showCreateDialog = false">×</button>
        </div>

        <div class="modal-body">
          <div class="form-group">
            <label class="form-label required">岗位名称</label>
            <input
              v-model="newJob.title"
              type="text"
              class="form-input"
              placeholder="例如：高级 Java 工程师"
            />
          </div>

          <div class="form-group">
            <label class="form-label">部门</label>
            <input
              v-model="newJob.department"
              type="text"
              class="form-input"
              placeholder="例如：技术部"
            />
          </div>

          <div class="form-group">
            <label class="form-label required">岗位描述</label>
            <textarea
              v-model="newJob.jd_content"
              class="form-textarea"
              rows="8"
              placeholder="请输入岗位职责和要求..."
            ></textarea>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="showCreateDialog = false">取消</button>
          <button class="btn-primary" @click="handleCreate" :disabled="creating">
            {{ creating ? '创建中...' : '创建岗位' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { jobApi } from '@/api'

const jobs = ref([])
const loading = ref(false)
const showCreateDialog = ref(false)
const creating = ref(false)
const newJob = ref({
  title: '',
  department: '',
  jd_content: ''
})

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

const loadJobs = async () => {
  loading.value = true
  try {
    const res = await jobApi.listJobs()
    jobs.value = res.data
  } catch (e) {
    ElMessage.error('加载岗位列表失败')
  } finally {
    loading.value = false
  }
}

const handleCreate = async () => {
  if (!newJob.value.title || !newJob.value.jd_content) {
    ElMessage.warning('请填写岗位名称和描述')
    return
  }

  creating.value = true
  try {
    await jobApi.createJob(newJob.value)
    ElMessage.success('创建成功')
    showCreateDialog.value = false
    loadJobs()
    newJob.value = { title: '', department: '', jd_content: '' }
  } catch (e) {
    ElMessage.error('创建失败')
  } finally {
    creating.value = false
  }
}

const handleDelete = async (id: string) => {
  if (!confirm('确定要删除这个岗位吗？')) {
    return
  }

  try {
    await jobApi.deleteJob(id)
    ElMessage.success('删除成功')
    loadJobs()
  } catch (e) {
    ElMessage.error('删除失败')
  }
}

onMounted(() => {
  loadJobs()
})
</script>

<style scoped>
.home-page {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: var(--space-8);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.page-title {
  font-family: var(--font-display);
  font-size: var(--text-3xl);
  font-weight: var(--font-bold);
  color: var(--color-text-primary);
  margin: 0 0 var(--space-2) 0;
}

.page-subtitle {
  font-size: var(--text-base);
  color: var(--color-text-secondary);
  margin: 0;
}

.btn-primary, .btn-secondary, .btn-danger {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-6);
  border-radius: var(--radius-base);
  font-size: var(--text-base);
  font-weight: var(--font-medium);
  border: none;
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
}

.btn-primary {
  background-color: var(--color-brand);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: var(--color-brand-light);
  transform: translateY(-1px);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: var(--color-surface);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
}

.btn-secondary:hover {
  background-color: var(--color-neutral-200);
}

.btn-danger {
  background-color: var(--color-error-bg);
  color: var(--color-error);
  border: 1px solid var(--color-error);
}

.btn-danger:hover {
  background-color: var(--color-error);
  color: white;
}

.btn-sm {
  padding: var(--space-2) var(--space-4);
  font-size: var(--text-sm);
}

.btn-icon {
  width: 18px;
  height: 18px;
}

.loading-state, .empty-state {
  text-align: center;
  padding: var(--space-16) var(--space-8);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--color-border);
  border-top-color: var(--color-brand);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto var(--space-4);
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-title {
  font-size: var(--text-xl);
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
  margin: 0 0 var(--space-2) 0;
}

.empty-text {
  font-size: var(--text-base);
  color: var(--color-text-secondary);
  margin: 0;
}

.jobs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: var(--space-6);
}

.job-card {
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-out);
}

.job-card:hover {
  border-color: var(--color-brand);
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.job-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--space-4);
  gap: var(--space-3);
}

.job-title {
  font-family: var(--font-display);
  font-size: var(--text-xl);
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
  margin: 0;
  flex: 1;
}

.job-status {
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-sm);
  white-space: nowrap;
}

.job-status.active {
  background-color: var(--color-success-bg);
  color: var(--color-success);
}

.job-status.closed {
  background-color: var(--color-neutral-200);
  color: var(--color-text-secondary);
}

.job-meta {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  margin-bottom: var(--space-4);
  padding-bottom: var(--space-4);
  border-bottom: 1px solid var(--color-border);
}

.meta-item {
  font-size: var(--text-sm);
}

.meta-label {
  color: var(--color-text-secondary);
}

.meta-value {
  color: var(--color-text-primary);
  font-weight: var(--font-medium);
}

.job-actions {
  display: flex;
  gap: var(--space-2);
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-modal-backdrop);
  padding: var(--space-4);
}

.modal-content {
  background-color: var(--color-surface);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-lg);
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  z-index: var(--z-modal);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-6);
  border-bottom: 1px solid var(--color-border);
}

.modal-title {
  font-family: var(--font-display);
  font-size: var(--text-2xl);
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  font-size: var(--text-3xl);
  color: var(--color-text-secondary);
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-base);
  transition: all var(--duration-fast);
}

.modal-close:hover {
  background-color: var(--color-neutral-200);
  color: var(--color-text-primary);
}

.modal-body {
  padding: var(--space-6);
  overflow-y: auto;
  flex: 1;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--space-3);
  padding: var(--space-6);
  border-top: 1px solid var(--color-border);
}

.form-group {
  margin-bottom: var(--space-5);
}

.form-group:last-child {
  margin-bottom: 0;
}

.form-label {
  display: block;
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--color-text-primary);
  margin-bottom: var(--space-2);
}

.form-label.required::after {
  content: ' *';
  color: var(--color-error);
}

.form-input, .form-textarea {
  width: 100%;
  padding: var(--space-3) var(--space-4);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-base);
  font-family: var(--font-body);
  font-size: var(--text-base);
  color: var(--color-text-primary);
  background-color: var(--color-bg);
  transition: all var(--duration-fast);
  box-sizing: border-box;
}

.form-input:focus, .form-textarea:focus {
  outline: none;
  border-color: var(--color-brand);
  box-shadow: 0 0 0 3px rgba(35, 80, 120, 0.1);
}

.form-textarea {
  resize: vertical;
  min-height: 120px;
}

@media (max-width: 768px) {
  .jobs-grid {
    grid-template-columns: 1fr;
  }
  .header-content {
    flex-direction: column;
    gap: var(--space-4);
  }
}
</style>
