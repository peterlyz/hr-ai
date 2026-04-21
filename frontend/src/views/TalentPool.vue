<template>
  <div class="talent-pool">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>企业人才库</span>
        </div>
      </template>
      
      <!-- 搜索筛选 -->
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" placeholder="姓名/公司/职位" />
        </el-form-item>
        <el-form-item label="技能">
          <el-input v-model="searchForm.skills" placeholder="多个技能用逗号分隔" />
        </el-form-item>
        <el-form-item label="工作年限">
          <el-select v-model="searchForm.min_experience" placeholder="不限">
            <el-option label="不限" :value="null" />
            <el-option label="1 年以上" :value="1" />
            <el-option label="3 年以上" :value="3" />
            <el-option label="5 年以上" :value="5" />
            <el-option label="10 年以上" :value="10" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="不限">
            <el-option label="不限" :value="null" />
            <el-option label="活跃" value="active" />
            <el-option label="暂不考虑" value="passive" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
      
      <!-- 人才列表 -->
      <el-table :data="talents" v-loading="loading">
        <el-table-column prop="candidate_name" label="姓名" />
        <el-table-column prop="current_company" label="当前公司" />
        <el-table-column prop="current_position" label="当前职位" />
        <el-table-column prop="years_of_experience" label="工作年限" />
        <el-table-column prop="highest_education" label="学历" />
        <el-table-column prop="best_score" label="最佳匹配分" width="100">
          <template #default="{ row }">
            <span v-if="row.best_score">{{ row.best_score.toFixed(1) }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="skills" label="技能标签" width="200">
          <template #default="{ row }">
            <el-tag v-for="skill in (row.skills || []).slice(0, 3)" :key="skill" size="small" style="margin-right: 5px">
              {{ skill }}
            </el-tag>
            <el-tag v-if="(row.skills || []).length > 3" size="small">+{{ (row.skills || []).length - 3 }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">
              {{ row.status === 'active' ? '活跃' : '暂不考虑' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button size="small" @click="showDetail(row.id)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.page_size"
        :total="pagination.total"
        :page-sizes="[20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        @current-change="loadTalents"
        @size-change="loadTalents"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>
    
    <!-- 人才详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="人才详情" width="700px">
      <div v-if="currentTalent">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="姓名">{{ currentTalent.candidate_name || '-' }}</el-descriptions-item>
          <el-descriptions-item label="当前公司">{{ currentTalent.current_company || '-' }}</el-descriptions-item>
          <el-descriptions-item label="当前职位">{{ currentTalent.current_position || '-' }}</el-descriptions-item>
          <el-descriptions-item label="工作年限">{{ currentTalent.years_of_experience || '-' }}年</el-descriptions-item>
          <el-descriptions-item label="学历">{{ currentTalent.highest_education || '-' }}</el-descriptions-item>
          <el-descriptions-item label="专业">{{ currentTalent.major || '-' }}</el-descriptions-item>
          <el-descriptions-item label="最佳匹配分" label-class-name="highlight">
            {{ currentTalent.best_score?.toFixed(1) || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="最佳匹配岗位">
            {{ currentTalent.best_match_job || '-' }}
          </el-descriptions-item>
        </el-descriptions>
        
        <el-divider>技能标签</el-divider>
        <el-tag v-for="skill in currentTalent.skills" :key="skill" style="margin-right: 10px; margin-bottom: 10px">
          {{ skill }}
        </el-tag>
        
        <el-divider>备注</el-divider>
        <el-input
          v-model="currentTalent.notes"
          type="textarea"
          :rows="4"
          placeholder="添加备注..."
        />
      </div>
      <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
        <el-button type="primary" @click="saveNotes" v-if="currentTalent">
          保存备注
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { talentApi } from '@/api'

const talents = ref([])
const loading = ref(false)
const showDetailDialog = ref(false)
const currentTalent = ref(null)

const searchForm = ref({
  keyword: '',
  skills: '',
  min_experience: null,
  status: null
})

const pagination = ref({
  page: 1,
  page_size: 20,
  total: 0
})

const loadTalents = async () => {
  loading.value = true
  try {
    const params = { ...searchForm.value, ...pagination.value }
    const res = await talentApi.listTalents(params)
    talents.value = res.data.data || []
    pagination.value.total = res.data.total || 0
  } catch (e) {
    ElMessage.error('加载人才库失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.value.page = 1
  loadTalents()
}

const resetSearch = () => {
  searchForm.value = {
    keyword: '',
    skills: '',
    min_experience: null,
    status: null
  }
  pagination.value.page = 1
  loadTalents()
}

const showDetail = async (id: string) => {
  try {
    const res = await talentApi.getTalent(id)
    currentTalent.value = res.data
    showDetailDialog.value = true
  } catch (e) {
    ElMessage.error('加载详情失败')
  }
}

const saveNotes = async () => {
  try {
    await talentApi.updateNotes(currentTalent.value.id, currentTalent.value.notes || '')
    ElMessage.success('保存成功')
    showDetailDialog.value = false
    loadTalents()
  } catch (e) {
    ElMessage.error('保存失败')
  }
}

onMounted(() => {
  loadTalents()
})
</script>

<style scoped>
.talent-pool {
  max-width: 1400px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

:deep(.highlight) {
  font-weight: bold;
  color: #409EFF;
}
</style>
