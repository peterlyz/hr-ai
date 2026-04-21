<template>
  <div class="job-detail">
    <el-card v-if="job">
      <template #header>
        <div class="card-header">
          <span>{{ job.title }}</span>
          <el-button @click="$router.push('/')">返回</el-button>
        </div>
      </template>
      
      <el-descriptions :column="2" border>
        <el-descriptions-item label="部门">{{ job.department || '-' }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="job.status === 'active' ? 'success' : 'info'">
            {{ job.status === 'active' ? '招聘中' : '已关闭' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="简历数量">{{ job.resume_count || 0 }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">
          {{ new Date(job.created_at).toLocaleString() }}
        </el-descriptions-item>
      </el-descriptions>
      
      <el-divider />
      
      <h3>岗位描述</h3>
      <div class="jd-content" v-html="formatJD(job.jd_content)" />
      
      <el-divider />
      
      <h3>评分规则</h3>
      <div v-if="(job.score_rules || []).length > 0">
        <el-collapse>
          <el-collapse-item
            v-for="(rule, index) in job.score_rules"
            :key="index"
            :title="`${rule.dimension} (${rule.weight}分)`"
          >
            <el-table :data="rule.criteria" :show-header="false" size="small">
              <el-table-column prop="condition" label="条件" />
              <el-table-column prop="score" label="得分" width="80" />
            </el-table>
          </el-collapse-item>
        </el-collapse>
      </div>
      <el-empty v-else description="暂无评分规则" />
    </el-card>
    
    <!-- 简历列表 -->
    <el-card style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <span>简历列表</span>
          <el-upload
            :action="uploadUrl"
            :multiple="true"
            :show-file-list="false"
            :on-success="handleUploadSuccess"
            :on-error="handleUploadError"
            accept=".pdf,.doc,.docx,.txt,.md"
          >
            <el-button type="primary">
              <el-icon><Upload /></el-icon>
              上传简历
            </el-button>
          </el-upload>
        </div>
      </template>
      
      <el-table :data="resumes" v-loading="loading" stripe>
        <el-table-column prop="candidate_name" label="候选人" />
        <el-table-column prop="file_type" label="类型" width="80" />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status_progress" label="进度" width="100">
          <template #default="{ row }">
            <el-progress :percentage="row.status_progress" :status="row.status === 'failed' ? 'exception' : undefined" />
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="上传时间" width="160">
          <template #default="{ row }">
            {{ new Date(row.created_at).toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250">
          <template #default="{ row }">
            <el-button size="small" @click="showResumeDetail(row)">
              详情
            </el-button>
            <el-button
              size="small"
              type="success"
              :disabled="!row.matching_result"
              @click="showScore(row)"
            >
              评分
            </el-button>
            <el-button
              size="small"
              type="primary"
              :disabled="!row.interview_questions || row.interview_questions.length === 0"
              @click="showQuestions(row)"
            >
              面试题
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 简历详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="简历详情" width="800px">
      <div v-if="currentResume">
        <el-tabs>
          <el-tab-pane label="基本信息">
            <el-descriptions :column="2" border v-if="currentResume.parsed_content">
              <el-descriptions-item label="姓名">
                {{ currentResume.parsed_content?.basic_info?.name || '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="学历">
                {{ currentResume.parsed_content?.basic_info?.education || '-' }}
              </el-descriptions-item>
            </el-descriptions>
            <el-empty v-else description="简历解析中或解析失败" />
          </el-tab-pane>
          <el-tab-pane label="原文内容">
            <div class="resume-raw">{{ currentResume?.raw_text || '暂无内容' }}</div>
          </el-tab-pane>
        </el-tabs>
      </div>
      <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
      </template>
    </el-dialog>
    
    <!-- 评分详情对话框 -->
    <el-dialog v-model="showScoreDialog" title="评分详情" width="700px">
      <div v-if="currentResume?.matching_result">
        <el-statistic title="总分" :value="currentResume.matching_result.total_score" />
        <el-divider />
        <h4>维度评分</h4>
        <el-table :data="currentResume.matching_result.dimension_scores" :show-header="false">
          <el-table-column prop="dimension" label="维度" />
          <el-table-column prop="score" label="得分" width="80" />
          <el-table-column prop="max_score" label="满分" width="80" />
        </el-table>
        <el-divider />
        <h4>评价总结</h4>
        <p>{{ currentResume.matching_result.summary }}</p>
        <el-divider />
        <h4>分析报告</h4>
        <div class="report-content">{{ currentResume.matching_result.analysis_report }}</div>
      </div>
      <template #footer>
        <el-button @click="showScoreDialog = false">关闭</el-button>
        <el-button type="primary" @click="exportReport">导出报告</el-button>
      </template>
    </el-dialog>
    
    <!-- 面试题目对话框 -->
    <el-dialog v-model="showQuestionsDialog" title="面试题目" width="800px" top="5vh">
      <div v-if="currentResume?.interview_questions && currentResume.interview_questions.length > 0">
        <el-collapse accordion>
          <el-collapse-item
            v-for="(q, index) in currentResume.interview_questions"
            :key="index"
            :title="`${index + 1}. [${getCategoryLabel(q.category)}] ${q.question.substr(0, 30)}...`"
          >
            <el-tag :type="getDifficultyType(q.difficulty)" style="margin-bottom: 10px">
              {{ getDifficultyLabel(q.difficulty) }}
            </el-tag>
            <h4>参考答案</h4>
            <p>{{ q.answer }}</p>
          </el-collapse-item>
        </el-collapse>
      </div>
      <template #footer>
        <el-button @click="showQuestionsDialog = false">关闭</el-button>
        <el-button type="primary" @click="exportQuestions">导出题目</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Upload } from '@element-plus/icons-vue'
import { useRoute } from 'vue-router'
import { resumeApi, matchingApi, interviewApi } from '@/api'

const route = useRoute()
const jobId = computed(() => route.params.id as string)

const job = ref(null)
const resumes = ref([])
const loading = ref(false)
const showDetailDialog = ref(false)
const showScoreDialog = ref(false)
const showQuestionsDialog = ref(false)
const currentResume = ref(null)

const uploadUrl = computed(() => `/api/resumes/upload?job_id=${jobId.value}`)

const loadJob = async () => {
  try {
    const res = await resumeApi.listResumes(jobId.value)
    resumes.value = res.data
  } catch (e) {
    ElMessage.error('加载简历列表失败')
  }
}

const getStatusType = (status: string) => {
  const types: any = {
    'uploading': 'info',
    'parsed': 'success',
    'matching': 'warning',
    'matched': 'success',
    'generating_questions': 'warning',
    'completed': 'success',
    'failed': 'danger'
  }
  return types[status] || 'info'
}

const getStatusText = (status: string) => {
  const texts: any = {
    'uploading': '上传中',
    'parsed': '解析完成',
    'matching': '匹配中',
    'matched': '匹配完成',
    'generating_questions': '生成题目',
    'completed': '完成',
    'failed': '失败'
  }
  return texts[status] || status
}

const showResumeDetail = async (resume: any) => {
  try {
    const res = await resumeApi.getResume(resume.id)
    currentResume.value = res.data
    showDetailDialog.value = true
  } catch (e) {
    ElMessage.error('加载详情失败')
  }
}

const showScore = async (resume: any) => {
  try {
    const res = await matchingApi.getDetail(resume.id)
    currentResume.value = { ...resume, matching_result: res.data }
    showScoreDialog.value = true
  } catch (e) {
    ElMessage.error('加载评分失败')
  }
}

const showQuestions = async (resume: any) => {
  try {
    const res = await interviewApi.getQuestions(resume.id)
    currentResume.value = { ...resume, interview_questions: res.data }
    showQuestionsDialog.value = true
  } catch (e) {
    ElMessage.error('加载题目失败')
  }
}

const exportReport = async () => {
  try {
    const res = await matchingApi.getReport(currentResume.value.id)
    const blob = new Blob([res.data], { type: 'text/plain;charset=utf-8' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `分析报告-${currentResume.value.candidate_name || currentResume.value.id}.txt`
    link.click()
  } catch (e) {
    ElMessage.error('导出失败')
  }
}

const exportQuestions = async () => {
  try {
    const res = await interviewApi.exportQuestions(currentResume.value.id, 'txt')
    const blob = new Blob([res.data], { type: 'text/plain;charset=utf-8' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `面试题目-${currentResume.value.candidate_name || currentResume.value.id}.txt`
    link.click()
  } catch (e) {
    ElMessage.error('导出失败')
  }
}

const handleUploadSuccess = () => {
  ElMessage.success('上传成功，开始解析')
  setTimeout(loadJob, 1000)
}

const handleUploadError = () => {
  ElMessage.error('上传失败')
}

const formatJD = (content: string) => {
  return content.replace(/\n/g, '<br>')
}

const getCategoryLabel = (category: string) => {
  const labels: any = {
    'technical': '技术能力',
    'behavioral': '行为面试',
    'cultural_fit': '文化匹配',
    'problem_solving': '解决问题'
  }
  return labels[category] || category
}

const getDifficultyLabel = (difficulty: string) => {
  const labels: any = {
    'easy': '简单',
    'medium': '中等',
    'hard': '困难'
  }
  return labels[difficulty] || difficulty
}

const getDifficultyType = (difficulty: string) => {
  const types: any = {
    'easy': 'success',
    'medium': 'warning',
    'hard': 'danger'
  }
  return types[difficulty] || 'info'
}

onMounted(() => {
  loadJob()
})
</script>

<style scoped>
.job-detail {
  max-width: 1400px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.jd-content {
  white-space: pre-wrap;
  line-height: 1.8;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 4px;
}

.resume-raw {
  white-space: pre-wrap;
  max-height: 500px;
  overflow-y: auto;
  font-family: monospace;
  font-size: 13px;
}

.report-content {
  white-space: pre-wrap;
  line-height: 1.8;
  max-height: 400px;
  overflow-y: auto;
}
</style>
