<template>
  <div class="requirement-detail">
    <el-page-header @back="goBack" :content="requirement?.title || '需求详情'" />
    
    <div class="content-wrapper" v-if="requirement">
      <el-row :gutter="20">
        <el-col :span="16">
          <div class="main-content">
            <el-card class="box-card">
              <template #header>
                <div class="card-header">
                  <span>需求信息</span>
                </div>
              </template>
              <div class="requirement-info">
                <p><strong>标题：</strong>{{ requirement.title }}</p>
                <p><strong>描述：</strong>{{ requirement.description || '无' }}</p>
                <p><strong>状态：</strong>{{ requirement.status }}</p>
                <p><strong>创建时间：</strong>{{ formatDate(requirement.created_at) }}</p>
              </div>
            </el-card>
            
            <el-card class="box-card" style="margin-top: 20px">
              <template #header>
                <div class="card-header">
                  <span>提交需求内容</span>
                </div>
              </template>
              <div class="content-submission">
                <el-form :model="contentForm" ref="contentFormRef">
                  <el-form-item label="文本内容">
                    <el-input 
                      v-model="contentForm.text" 
                      type="textarea" 
                      :rows="4"
                      placeholder="请输入文本内容"
                    />
                  </el-form-item>
                  
                  <el-form-item label="上传文件">
                    <el-upload
                      class="upload-demo"
                      action="/api/requirements/upload"
                      :auto-upload="false"
                      :on-change="handleFileChange"
                      :limit="1"
                    >
                      <el-button slot="trigger" size="small" type="primary">选取文件</el-button>
                      <div slot="tip" class="el-upload__tip">支持图片和音频文件，大小不超过16MB</div>
                    </el-upload>
                  </el-form-item>
                  
                  <el-form-item>
                    <el-button 
                      type="primary" 
                      @click="submitContent"
                      :loading="submitting"
                    >
                      提交内容
                    </el-button>
                  </el-form-item>
                </el-form>
              </div>
            </el-card>
            
            <el-card class="box-card" style="margin-top: 20px">
              <template #header>
                <div class="card-header">
                  <span>已提交内容</span>
                </div>
              </template>
              <div class="submitted-content">
                <div v-if="submittedContents.length === 0" class="empty">
                  暂无提交的内容
                </div>
                <div v-else>
                  <div 
                    v-for="content in submittedContents" 
                    :key="content.id" 
                    class="content-item"
                  >
                    <div class="content-header">
                      <span class="content-type">{{ getContentTypeName(content.content_type) }}</span>
                      <span class="submit-time">{{ formatDate(content.submitted_at) }}</span>
                    </div>
                    <div class="content-body">
                      <p v-if="content.content_type === 'text'">{{ content.content_text }}</p>
                      <div v-else-if="content.content_type === 'image'">
                        <el-image 
                          :src="content.file_path" 
                          style="width: 200px; height: 200px"
                          :preview-src-list="[content.file_path]"
                        />
                      </div>
                      <div v-else-if="content.content_type === 'audio'">
                        <audio :src="content.file_path" controls />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </el-card>
          </div>
        </el-col>
        
        <el-col :span="8">
          <el-card class="box-card">
            <template #header>
              <div class="card-header">
                <span>参与者</span>
                <el-button 
                  v-if="isOwner" 
                  style="float: right; padding: 3px 0" 
                  type="text"
                  @click="showInviteDialog = true"
                >
                  邀请成员
                </el-button>
              </div>
            </template>
            <div class="participants">
              <div 
                v-for="participant in participants" 
                :key="participant.id" 
                class="participant-item"
              >
                <el-avatar :size="30">{{ participant.username.charAt(0).toUpperCase() }}</el-avatar>
                <span class="participant-name">{{ participant.username }}</span>
                <span class="participant-role" :class="participant.role">{{ getRoleName(participant.role) }}</span>
              </div>
            </div>
          </el-card>
          
          <el-card class="box-card" style="margin-top: 20px">
            <template #header>
              <div class="card-header">
                <span>生成文档</span>
              </div>
            </template>
            <div class="document-generation">
              <el-button 
                type="primary" 
                @click="generateDocument"
                :loading="generating"
                style="width: 100%"
              >
                生成需求文档
              </el-button>
              <el-button 
                v-if="generatedDocument" 
                @click="downloadDocument"
                style="width: 100%; margin-top: 10px"
              >
                下载文档
              </el-button>
              <div v-if="generatedDocument" class="document-preview">
                <h4>文档预览</h4>
                <div class="document-content">
                  {{ generatedDocument }}
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <!-- 邀请成员对话框 -->
    <el-dialog v-model="showInviteDialog" title="邀请成员" width="500px">
      <el-form>
        <el-form-item label="用户邮箱">
          <el-input 
            v-model="inviteEmail" 
            placeholder="请输入用户邮箱"
            clearable
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showInviteDialog = false">取消</el-button>
          <el-button type="primary" @click="inviteMember">邀请</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore, useRequirementStore } from '../store'
import axios from 'axios'

export default {
  name: 'RequirementDetail',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const userStore = useUserStore()
    const requirementStore = useRequirementStore()
    
    const requirement = ref(null)
    const participants = ref([])
    const submittedContents = ref([])
    const isOwner = ref(false)
    
    const contentForm = ref({
      text: '',
      file: null
    })
    
    const submitting = ref(false)
    const generating = ref(false)
    
    const showInviteDialog = ref(false)
    const inviteEmail = ref('')
    
    const generatedDocument = ref('')
    
    const goBack = () => {
      router.push('/dashboard')
    }
    
    const formatDate = (dateString) => {
      const date = new Date(dateString)
      return date.toLocaleDateString('zh-CN') + ' ' + date.toLocaleTimeString('zh-CN')
    }
    
    const getContentTypeName = (type) => {
      const types = {
        'text': '文本',
        'image': '图片',
        'audio': '音频'
      }
      return types[type] || type
    }
    
    const getRoleName = (role) => {
      const roles = {
        'owner': '创建者',
        'member': '成员'
      }
      return roles[role] || role
    }
    
    const handleFileChange = (file) => {
      contentForm.value.file = file.raw
    }
    
    const submitContent = async () => {
      submitting.value = true
      try {
        const formData = new FormData()
        if (contentForm.value.text) {
          formData.append('text', contentForm.value.text)
        }
        if (contentForm.value.file) {
          formData.append('file', contentForm.value.file)
        }
        
        const response = await axios.post(
          `/api/requirements/${route.params.id}/submit`, 
          formData,
          {
            headers: {
              'Content-Type': 'multipart/form-data'
            }
          }
        )
        
        // 添加到已提交内容列表
        submittedContents.value.push(response.data.content)
        
        // 重置表单
        contentForm.value.text = ''
        contentForm.value.file = null
      } catch (error) {
        console.error('提交内容失败:', error)
        alert('提交内容失败')
      } finally {
        submitting.value = false
      }
    }
    
    const generateDocument = async () => {
      generating.value = true
      try {
        // 调用API生成文档
        const response = await axios.post(`/api/requirements/${route.params.id}/generate-document`)
        generatedDocument.value = response.data.document
      } catch (error) {
        console.error('生成文档失败:', error)
        alert('生成文档失败')
      } finally {
        generating.value = false
      }
    }
    
    const downloadDocument = async () => {
      try {
        // 调用API下载PDF文档
        const response = await axios.get(`/api/requirements/${route.params.id}/export-pdf`, {
          responseType: 'blob'
        })
        
        // 创建下载链接
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `requirement-${route.params.id}.pdf`)
        document.body.appendChild(link)
        link.click()
        link.remove()
      } catch (error) {
        console.error('下载文档失败:', error)
        alert('下载文档失败')
      }
    }
    
    const inviteMember = async () => {
      try {
        // 这里应该调用API邀请成员
        // const response = await axios.post(`/api/requirements/${route.params.id}/invite`, {
        //   email: inviteEmail.value
        // })
        
        alert('邀请成员功能待实现')
        showInviteDialog.value = false
        inviteEmail.value = ''
      } catch (error) {
        console.error('邀请成员失败:', error)
        alert('邀请成员失败')
      }
    }
    
    // 获取需求详情
    const fetchRequirementDetail = async () => {
      try {
        console.log('Fetching requirement detail for ID:', route.params.id)
        const response = await axios.get(`/api/requirements/${route.params.id}`)
        console.log('Requirement detail response:', response.data)
        requirement.value = response.data.requirement
        
        // 检查是否为创建者
        if (userStore.userInfo && requirement.value) {
          isOwner.value = requirement.value.creator_id === userStore.userInfo.id
        }
      } catch (error) {
        console.error('获取需求详情失败:', error.response?.data || error.message)
        alert('获取需求详情失败: ' + (error.response?.data?.message || error.message))
      }
    }
    
    // 获取参与者列表
    const fetchParticipants = async () => {
      try {
        console.log('Fetching participants for requirement ID:', route.params.id)
        const response = await axios.get(`/api/requirements/${route.params.id}/participants`)
        console.log('Participants response:', response.data)
        participants.value = response.data.participants
      } catch (error) {
        console.error('获取参与者列表失败:', error.response?.data || error.message)
        alert('获取参与者列表失败: ' + (error.response?.data?.message || error.message))
      }
    }
    
    // 获取已提交内容
    const fetchSubmittedContents = async () => {
      try {
        console.log('Fetching submitted contents for requirement ID:', route.params.id)
        const response = await axios.get(`/api/requirements/${route.params.id}/contents`)
        console.log('Submitted contents response:', response.data)
        submittedContents.value = response.data.contents
      } catch (error) {
        console.error('获取已提交内容失败:', error.response?.data || error.message)
        alert('获取已提交内容失败: ' + (error.response?.data?.message || error.message))
      }
    }
    
    onMounted(() => {
      fetchRequirementDetail()
      fetchParticipants()
      fetchSubmittedContents()
    })
    
    return {
      requirement,
      participants,
      submittedContents,
      isOwner,
      contentForm,
      submitting,
      generating,
      showInviteDialog,
      inviteEmail,
      generatedDocument,
      goBack,
      formatDate,
      getContentTypeName,
      getRoleName,
      handleFileChange,
      submitContent,
      generateDocument,
      downloadDocument,
      inviteMember
    }
  }
}
</script>

<style scoped>
.requirement-detail {
  padding: 20px;
}

.content-wrapper {
  margin-top: 20px;
}

.box-card {
  border-radius: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.requirement-info p {
  margin: 10px 0;
}

.content-item {
  border-bottom: 1px solid #eee;
  padding: 15px 0;
}

.content-item:last-child {
  border-bottom: none;
}

.content-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.content-type {
  font-weight: bold;
  color: #409eff;
}

.submit-time {
  color: #999;
  font-size: 12px;
}

.participant-item {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.participant-name {
  margin-left: 10px;
  flex: 1;
}

.participant-role {
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 4px;
}

.participant-role.owner {
  background-color: #f0f9eb;
  color: #67c23a;
}

.participant-role.member {
  background-color: #ecf5ff;
  color: #409eff;
}

.document-preview {
  margin-top: 20px;
  padding: 15px;
  background-color: #f5f5f5;
  border-radius: 4px;
}

.document-content {
  white-space: pre-wrap;
  line-height: 1.6;
}

.empty {
  text-align: center;
  color: #999;
  padding: 20px;
}
</style>