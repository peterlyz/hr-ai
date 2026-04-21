import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 60000
})

export const aiApi = {
  listModels: () => api.get('/ai-models/'),
  createModel: (data: any) => api.post('/ai-models/', data),
  getModel: (id: string) => api.get(`/ai-models/${id}`),
  updateModel: (id: string, data: any) => api.put(`/ai-models/${id}`, data),
  deleteModel: (id: string) => api.delete(`/ai-models/${id}`),
  testModel: (id: string) => api.get(`/ai-models/${id}/test`)
}

export const jobApi = {
  listJobs: () => api.get('/jobs/'),
  createJob: (data: any) => api.post('/jobs/', data),
  getJob: (id: string) => api.get(`/jobs/${id}`),
  updateJob: (id: string, data: any) => api.put(`/jobs/${id}`, data),
  deleteJob: (id: string) => api.delete(`/jobs/${id}`),
  setScoreRules: (jobId: string, rules: any) => api.post(`/jobs/${jobId}/score-rules`, rules)
}

export const resumeApi = {
  uploadResumes: (jobId: string, files: File[]) => {
    const formData = new FormData()
    formData.append('job_id', jobId)
    files.forEach(file => formData.append('files', file))
    return api.post('/resumes/upload', formData)
  },
  listResumes: (jobId: string) => api.get(`/resumes/?job_id=${jobId}`),
  getResume: (id: string) => api.get(`/resumes/${id}`),
  getResumeStatus: (id: string) => api.get(`/resumes/${id}/status`),
  pollStatus: async (resumeId: string): Promise<any> => {
    return new Promise((resolve, reject) => {
      const check = async () => {
        try {
          const res = await resumeApi.getResumeStatus(resumeId)
          if (['completed', 'failed'].includes(res.data.status)) {
            resolve(res.data)
          } else {
            setTimeout(check, 2000)
          }
        } catch (e) {
          reject(e)
        }
      }
      check()
    })
  }
}

export const matchingApi = {
  getResults: (jobId: string) => api.get(`/matching/results/${jobId}`),
  getDetail: (resumeId: string) => api.get(`/matching/results/${resumeId}/detail`),
  getReport: (resumeId: string) => api.get(`/matching/results/${resumeId}/report`)
}

export const interviewApi = {
  getQuestions: (resumeId: string) => api.get(`/interviews/questions/${resumeId}`),
  exportQuestions: (resumeId: string, format: string = 'txt') => 
    api.get(`/interviews/questions/${resumeId}/export?format=${format}`)
}

export const talentApi = {
  listTalents: (params: any) => api.get('/talent-pool/', { params }),
  getTalent: (id: string) => api.get(`/talent-pool/${id}`),
  addTags: (id: string, tags: string[]) => api.post(`/talent-pool/${id}/tags`, { tags }),
  updateNotes: (id: string, notes: string) => api.post(`/talent-pool/${id}/notes`, { notes }),
  addToPool: (resumeId: string) => api.post(`/talent-pool/resumes/${resumeId}/add`)
}
