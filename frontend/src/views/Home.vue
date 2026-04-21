<template>
  <div class="home">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>岗位列表</span>
          <el-button type="primary" @click="showCreateDialog = true">
            <el-icon><Plus /></el-icon>
            新建岗位
          </el-button>
        </div>
      </template>
      
      <el-table :data="jobs" style="width: 100%" v-loading="loading">
        <el-table-column prop="title" label="岗位名称" />
        <el-table-column prop="department" label="部门" />
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">
              {{ row.status === 'active' ? '招聘中' : '已关闭' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间">
          <template #default="{ row }">
            {{ new Date(row.created_at).toLocaleDateString() }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" @click="$router.push(`/job/${row.id}`)">
              查看详情
            </el-button>
            <el-button size="small" type="danger" @click="handleDelete(row.id)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 创建岗位对话框 -->
    <el-dialog v-model="showCreateDialog" title="新建岗位" width="600px">
      <el-form :model="newJob" label-width="80px">
        <el-form-item label="岗位名称" required>
          <el-input v-model="newJob.title" placeholder="例如：高级 Java 工程师" />
        </el-form-item>
        <el-form-item label="部门">
          <el-input v-model="newJob.department" placeholder="例如：技术部" />
        </el-form-item>
        <el-form-item label="岗位描述" required>
          <el-input
            v-model="newJob.jd_content"
            type="textarea"
            :rows="8"
            placeholder="请输入岗位职责和要求..."
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleCreate" :loading="creating">
          创建
        </el-button>
      </template>
    </el-dialog>
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
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.home {
  max-width: 1200px;
  margin: 0 auto;
}
</style>
