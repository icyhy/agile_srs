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
                  <el-button 
                    v-if="isOwner" 
                    style="float: right; padding: 3px 0" 
                    type="text"
                    @click="startEditing"
                  >
                    编辑
                  </el-button>
                </div>
              </template>
              <div class="requirement-info">
                <div v-if="!isEditing">
                  <p><strong>标题：</strong>{{ requirement.title }}</p>
                  <p><strong>描述：</strong>{{ requirement.description || '无' }}</p>
                  <p><strong>状态：</strong>{{ requirement.status }}</p>
                  <p><strong>创建者：</strong>{{ requirement.creator_name }}</p>

              </div>
                <div v-else>
                  <el-form :model="editForm" ref="editFormRef">
                    <el-form-item label="标题">
                      <el-input v-model="editForm.title" />
                    </el-form-item>
                    <el-form-item label="描述">
                      <el-input v-model="editForm.description" type="textarea" />
                    </el-form-item>
                    <el-form-item label="状态">
                      <el-select v-model="editForm.status">
                        <el-option label="草稿" value="draft" />
                        <el-option label="完成" value="completed" />
                      </el-select>
                    </el-form-item>
                    <el-form-item>
                      <el-button type="primary" @click="saveEdit">保存</el-button>
                      <el-button @click="cancelEdit">取消</el-button>
                    </el-form-item>
                  </el-form>
                </div>
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
                    <div class="markdown-editor-wrapper">
                      <!-- Vditor编辑器容器 -->
                      <div id="vditor-editor"></div>
                    </div>
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
                    <span class="content-type">
                      <el-tooltip v-if="content.content_type === 'markdown'" content="预览Markdown" placement="top">
                        <el-button type="text" @click="showPreviewDialog(content)" style="padding: 0">
                          <FontAwesomeIcon icon="fa-eye" class="icon-preview" />
                        </el-button>
                      </el-tooltip>
                      <el-tooltip v-else-if="content.content_type === 'text'" content="文本内容" placement="top">
                        <FontAwesomeIcon icon="fa-file-text" class="icon-type" />
                      </el-tooltip>
                      <el-tooltip v-else-if="content.content_type === 'image'" content="图片" placement="top">
                        <FontAwesomeIcon icon="fa-image" class="icon-type" />
                      </el-tooltip>
                      <el-tooltip v-else-if="content.content_type === 'audio'" content="音频" placement="top">
                        <FontAwesomeIcon icon="fa-microphone" class="icon-type" />
                      </el-tooltip>
                      <el-tooltip v-else content="文件" placement="top">
                        <FontAwesomeIcon icon="fa-file" class="icon-type" />
                      </el-tooltip>
                      <!-- 删除按钮 -->
                      <template v-if="userStore.userInfo && parseInt(userStore.userInfo.id) === parseInt(content.submitted_by)">
                        <el-button type="text" size="small" class="delete-btn" @click="deleteContent(content.id)">
                          <FontAwesomeIcon icon="fa-trash-can" />
                        </el-button>
                      </template>
                    </span>
                    <span class="submit-time">{{ formatDate(content.submitted_at) }}</span>

                  </div>
                  <div class="content-body">
                    <p v-if="content.content_type === 'text' || content.content_type === 'markdown'">
                      {{ truncateText(content.content_text, 50) }}
                    </p>
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
                <el-button 
                  v-if="isOwner && participant.id !== userStore.userInfo.id"
                  type="text" 
                  size="small" 
                  class="remove-btn"
                  @click="showRemoveConfirm(participant.id, participant.username)"
                >
                  删除
                </el-button>
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
                @click="generateDocumentHandler"
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
                <div class="version-selector">
                  <span>文档版本：</span>
                  <el-select v-model="currentVersion" @change="switchDocumentVersion">
                    <el-option
                      v-for="version in documentVersions"
                      :key="version.version"
                      :label="`版本 ${version.version} (${formatDate(version.generated_at)})`"
                      :value="version.version"
                    />
                  </el-select>
                </div>
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
            @input="handleEmailInput"
            @blur="handleEmailBlur"
          />
          <!-- 邮箱候选列表 -->
          <div v-if="emailSuggestions.length > 0 && showSuggestions" class="email-suggestions">
            <div 
              v-for="suggestion in emailSuggestions" 
              :key="suggestion.id"
              class="suggestion-item" 
              @click="selectEmailSuggestion(suggestion.email)"
              @mouseenter="hoveredSuggestion = suggestion.id"
              :class="{ 'hovered': hoveredSuggestion === suggestion.id }"
            >
              {{ suggestion.email }} ({{ suggestion.username }})
            </div>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showInviteDialog = false">取消</el-button>
          <el-button type="primary" @click="inviteMember">邀请</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 删除参与者确认对话框 -->
    <el-dialog v-model="showRemoveConfirmDialog" title="确认删除" width="500px">
      <p>确定要从参与者列表中删除 <strong>{{ removeConfirmUsername }}</strong> 吗？</p>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showRemoveConfirmDialog = false">取消</el-button>
          <el-button type="primary" class="danger-btn" @click="removeParticipant">确定删除</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 内容预览对话框 -->
    <el-dialog v-model="previewDialogVisible" :title="previewContentTitle" width="800px" height="600px">
      <div v-if="previewContentType === 'markdown'" class="markdown-preview" v-html="renderMarkdown(previewContent)"></div>
      <div v-else-if="previewContentType === 'text'" class="text-preview">
        {{ previewContent }}
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="previewDialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 内容删除确认对话框 -->
    <el-dialog v-model="showDeleteContentDialog" title="确认删除" width="500px">
      <p>确定要删除该提交内容吗？</p>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showDeleteContentDialog = false">取消</el-button>
          <el-button type="primary" class="danger-btn" @click="confirmDeleteContent">确定删除</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore, useRequirementStore } from '../store'
import api, { generateDocument, exportPdf, exportMarkdown, getDocumentVersions, getDocumentByVersion, getUserByEmail, searchUsersByEmail } from '../utils/api'
import { ElMessage } from 'element-plus'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
// Markdown支持库
import { marked } from 'marked'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'



// 导入Vditor相关组件
import Vditor from 'vditor';
import 'vditor/dist/index.css';

// 初始化路由
const route = useRoute()
const router = useRouter()

// 初始化store
const userStore = useUserStore()

// 初始化Vditor编辑器的函数
const initVditor = (elementId, contentForm) => {
  return new Vditor(elementId, {
    height: 360,
    value: contentForm.text || '',
    mode: 'wysiwyg', // 默认使用所见即所得模式
    preview: {
      theme: {
        current: 'light'
      }
    },
    cache: {
      enable: false
    },
    toolbar: [
      'bold', 'italic', 'strike', '|',
      'headings', '|',
      'list', 'ordered-list', 'check', 'outdent', 'indent', '|',
      'link',
      {
        name: 'image',
        tip: '插入图片',
        className: 'vditor-toolbar-icon vditor-toolbar-icon-image',
        icon: '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg>',
        click: function(editor) {
          const input = document.createElement('input');
          input.type = 'file';
          input.accept = 'image/*';
          input.onchange = function(e) {
            if (e.target.files && e.target.files[0]) {
              const file = e.target.files[0];
              const reader = new FileReader();
              reader.onload = function(event) {
                editor.insertValue(`![${file.name}](${event.target.result})`);
              };
              reader.readAsDataURL(file);
            }
          };
          input.click();
        }
      },
      '|',
      'table', '|',
      'code',
      {
        name: 'code-block',
        tip: '代码块',
        className: 'vditor-toolbar-icon vditor-toolbar-icon-code-block',
        icon: '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"></polyline><polyline points="8 6 2 12 8 18"></polyline></svg>'
      },
      '|',
      'undo', 'redo', '|'
    ],
    upload: {
      accept: 'image/*',
      url: '/api/requirements/upload',
      filename (name) {
        return name;
      },
      linkToImgUrl: '/api/requirements/upload',
      success (editor, msg) {
        const resp = JSON.parse(msg);
        editor.insertValue(`![${resp.data.name}](${resp.data.url})`);
      }
    },
    callback: {
      change: (value) => {
        contentForm.value.text = value;
      }
    }
  });
};

// 响应式数据
const requirement = ref({});
const participants = ref([]);
const submittedContents = ref([]);
const isEditing = ref(false);

const fileList = ref([]);

// 编辑表单数据
const requirementForm = ref({
  title: '',
  description: '',
  status: '',
  due_date: '',
  content_type: 'markdown',
  priority: ''
});

// 对话框相关数据
const showInviteDialog = ref(false);
const inviteEmail = ref('');
const emailSuggestions = ref([]);
const showSuggestions = ref(false);
const hoveredSuggestion = ref(null);
const searchTimeout = ref(null);
const showRemoveConfirmDialog = ref(false);
const removeConfirmUserId = ref('');
const removeConfirmUsername = ref('');
// 预览弹窗相关数据
const previewDialogVisible = ref(false);
const previewContent = ref('');
const previewContentType = ref('');
const previewContentTitle = ref('');
// 删除确认对话框
const showDeleteContentDialog = ref(false);
const deleteContentId = ref('');
const deleteContentTitle = ref('');

// 文档相关数据
const generatedDocument = ref('');
const documentVersions = ref([]);
const currentVersion = ref(null);
const submitting = ref(false);
const generating = ref(false);

const isOwner = ref(false)
const editForm = ref({
  title: '',
  description: '',
  status: 'draft'
});
const contentForm = ref({
  text: '',
  file: null
});
const uploadImagePreview = ref('')
const pastedImages = ref([])
// Vditor实例引用
const vditor = ref(null);

// 初始化marked配置，支持代码高亮
marked.setOptions({
  highlight: function(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      return hljs.highlight(code, { language: lang }).value;
    }
    return hljs.highlightAuto(code).value;
  },
  breaks: true,
  gfm: true,
  tables: true,
  sanitize: false
});




// 保存编辑方法
const saveEdit = async () => {
  try {
    const response = await api.put(`/requirements/${route.params.id}`, {
      title: requirementForm.value.title,
      description: requirementForm.value.description,
      status: requirementForm.value.status,
      due_date: requirementForm.value.due_date,
      content_type: requirementForm.value.content_type,
      priority: requirementForm.value.priority
    });
    
    ElMessage.success('需求更新成功');
    isEditing.value = false;
    await fetchRequirementDetail();
  } catch (error) {
    ElMessage.error('需求更新失败');
    console.error('更新需求失败:', error);
  }
};

// 日期格式化函数
const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  });
};

// 获取内容类型名称
const getContentTypeName = (type) => {
  const types = {
    'text': '文本',
    'markdown': 'Markdown',
    'html': 'HTML'
  };
  return types[type] || type;
};

// 截断文本函数，保留指定长度的字符
const truncateText = (text, maxLength = 50) => {
  if (!text || text.length <= maxLength) {
    return text;
  }
  return text.substring(0, maxLength) + '...';
};

// 获取角色名称
const getRoleName = (role) => {
  const roles = {
    'admin': '管理员',
    'editor': '编辑者',
    'viewer': '查看者'
  };
  return roles[role] || role;
};

// 文件变更处理
const handleFileChange = (event) => {
  const file = event.target.files[0];
  if (file) {
    fileList.value.push(file);
  }
};

// 返回上一页函数
const goBack = () => {
  router.back();
};

// 提交内容方法
const submitContent = async () => {
  submitting.value = true;
  try {
    const formData = new FormData();
    // 使用Vditor的getValue()函数直接获取编辑器内容
    const markdownContent = vditor.value ? vditor.value.getValue() : '';
    formData.append('text', markdownContent);
    // 明确设置内容类型为markdown
    formData.append('content_type', 'markdown');
    
    // 添加文件（后端期望单个文件，键名为'file'）
    if (fileList.value.length > 0) {
      formData.append('file', fileList.value[0]);
    }
    
    // 上传内容和文件
    const response = await api.post(`/requirements/${route.params.id}/submit`, formData);
    
    ElMessage.success('内容提交成功');
    // 清空表单和文件列表
    if (vditor.value) {
      vditor.value.setValue('');
    }
    contentForm.value.text = '';
    fileList.value = [];
    // 重新获取已提交内容
    await fetchSubmittedContents();
  } catch (error) {
    ElMessage.error('内容提交失败');
    console.error('提交内容失败:', error);
  } finally {
    submitting.value = false;
  }
};

const fetchDocumentVersions = async () => {
  try {
    const response = await getDocumentVersions(route.params.id)
    documentVersions.value = response.data.documents
    // 如果有版本，默认选中最新版本
    if (documentVersions.value.length > 0) {
      const latestVersion = documentVersions.value[0]
      currentVersion.value = latestVersion.version
      generatedDocument.value = latestVersion.content
    }
  } catch (error) {
    console.error('获取文档版本列表失败:', error)
  }
}

const generateDocumentHandler = async () => {
  generating.value = true
  try {
    console.log('开始生成文档，需求ID:', route.params.id)
    const response = await generateDocument(route.params.id)
    console.log('文档生成API调用成功')
    generatedDocument.value = response.data.document
    currentVersion.value = response.data.version
    // 刷新版本列表
    await fetchDocumentVersions()
    console.log('文档版本更新成功')
    ElMessage.success('文档生成成功')
  } catch (error) {
    console.error('生成文档失败:', {
      message: error.message,
      response: error.response?.data,
      status: error.response?.status,
      fullError: error
    })
    // 显示更具体的错误信息给用户
    let errorMessage = '生成文档失败'
    if (error.response?.data?.message) {
      errorMessage = error.response.data.message
    } else if (error.response?.status === 401) {
      errorMessage = '认证失败：LLM API密钥无效或过期，请检查配置'
    } else if (error.response?.status === 404) {
      errorMessage = '需求不存在或已被删除'
    } else if (error.response?.status >= 500) {
      errorMessage = error.response?.data?.error || '服务器暂时无法处理请求，请稍后重试'
    } else if (error.message) {
      errorMessage = error.message
    }
    ElMessage.error(errorMessage)
  } finally {
    generating.value = false
  }
}

const switchDocumentVersion = async (version) => {
  try {
    const response = await getDocumentByVersion(route.params.id, version)
    generatedDocument.value = response.data.document.content
    currentVersion.value = version
  } catch (error) {
    console.error('切换文档版本失败:', error)
    ElMessage.error('切换文档版本失败')
  }
}

const downloadDocument = async () => {
  try {
    // 调用API下载Markdown文档
    const response = await exportMarkdown(route.params.id)
    
    // 创建下载链接
    const url = window.URL.createObjectURL(new Blob([response.data], { type: 'text/markdown' }))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `requirement-${route.params.id}-v${currentVersion.value}.md`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    
    ElMessage.success('Markdown文档下载成功')
  } catch (error) {
    console.error('下载文档失败:', error)
    ElMessage.error('下载Markdown文档失败')
  }
}
const inviteMember = async () => {
  try {
    // 验证邮箱不为空
    if (!inviteEmail.value.trim()) {
      ElMessage.error('请输入有效的邮箱地址')
      return
    }
    
    // 根据邮箱查找用户
    const userResponse = await getUserByEmail(inviteEmail.value)
    const user = userResponse.data.user
    
    if (!user) {
      ElMessage.error('未找到该邮箱对应的用户')
      return
    }
    
    // 检查用户是否已经是参与者
    const isAlreadyParticipant = participants.value.some(p => p.id === user.id)
    if (isAlreadyParticipant) {
      ElMessage.warning('该用户已经是项目参与者')
      showInviteDialog.value = false
      inviteEmail.value = ''
      return
    }
    
    // 调用API邀请成员
    const response = await api.post(`/requirements/${route.params.id}/invite`, {
      user_ids: [user.id]
    })
    
    ElMessage.success(`邀请用户${user.username}成功`)
    
    // 关闭对话框并重置输入
    showInviteDialog.value = false
    inviteEmail.value = ''
    
    // 刷新参与者列表
    fetchParticipants()
  } catch (error) {
    console.error('邀请成员失败:', error)
    ElMessage.error('邀请成员失败: ' + (error.response?.data?.message || error.message))
  }
}

// 获取需求详情
const fetchRequirementDetail = async () => {
  try {
    console.log('Fetching requirement detail for ID:', route.params.id)
    const response = await api.get(`/requirements/${route.params.id}`)
    console.log('Requirement detail response:', response.data)
    requirement.value = response.data.requirement
    
    // 检查是否为创建者
    console.log('User info:', userStore.userInfo);
    console.log('Requirement creator_id:', requirement.value?.creator_id);
    console.log('User ID:', userStore.userInfo?.id);
    if (userStore.userInfo && requirement.value) {
      // 添加类型检查
      console.log('Creator ID type:', typeof requirement.value.creator_id, 'Value:', requirement.value.creator_id);
      console.log('User ID type:', typeof userStore.userInfo.id, 'Value:', userStore.userInfo.id);
      // Ensure both values are of the same type for comparison
      const creatorId = parseInt(requirement.value.creator_id);
      const userId = parseInt(userStore.userInfo.id);
      console.log('Parsed Creator ID:', creatorId, 'Type:', typeof creatorId);
      console.log('Parsed User ID:', userId, 'Type:', typeof userId);
      isOwner.value = creatorId === userId;
      console.log('Is owner:', isOwner.value);
      console.log('Comparison result:', creatorId, '===', userId, '=', isOwner.value);
    } else {
      console.log('Missing user info or requirement data');
    }
  } catch (error) {
    console.error('获取需求详情失败:', error.response?.data || error.message)
    ElMessage.error('获取需求详情失败: ' + (error.response?.data?.message || error.message))
  }
}

// 获取参与者列表
const fetchParticipants = async () => {
  try {
    console.log('Fetching participants for requirement ID:', route.params.id)
    const response = await api.get(`/requirements/${route.params.id}/participants`)
    console.log('Participants response:', response.data)
    participants.value = response.data.participants
  } catch (error) {
    console.error('获取参与者列表失败:', error.response?.data || error.message)
    ElMessage.error('获取参与者列表失败: ' + (error.response?.data?.message || error.message))
  }
}

// 获取已提交内容
const fetchSubmittedContents = async () => {
  try {
    console.log('Fetching submitted contents for requirement ID:', route.params.id)
    const response = await api.get(`/requirements/${route.params.id}/contents`)
    console.log('Submitted contents response:', response.data)
    submittedContents.value = response.data.contents
  } catch (error) {
    console.error('获取已提交内容失败:', error.response?.data || error.message)
    ElMessage.error('获取已提交内容失败: ' + (error.response?.data?.message || error.message))
  }
}

// 处理邮箱输入
const handleEmailInput = (value) => {
  // 清除之前的定时器
  if (searchTimeout.value) {
    clearTimeout(searchTimeout.value)
  }
  
  // 输入不为空且至少有3个字符时进行搜索
  if (value && value.trim().length >= 2) {
    searchTimeout.value = setTimeout(() => {
      searchEmailSuggestions(value)
    }, 300) // 延迟300ms搜索，避免频繁请求
  } else {
    showSuggestions.value = false
    emailSuggestions.value = []
  }
}

// 根据邮箱前缀搜索用户
const searchEmailSuggestions = async (emailPrefix) => {
  try {
    const response = await searchUsersByEmail(emailPrefix)
    emailSuggestions.value = response.data.users
    showSuggestions.value = emailSuggestions.value.length > 0
  } catch (error) {
    console.error('搜索用户失败:', error)
    emailSuggestions.value = []
    showSuggestions.value = false
  }
}

// 选择邮箱候选项
const selectEmailSuggestion = (email) => {
  inviteEmail.value = email
  showSuggestions.value = false
  emailSuggestions.value = []
}

// 处理输入框失去焦点
const handleEmailBlur = () => {
  // 延迟隐藏，以便可以点击候选项
  setTimeout(() => {
    showSuggestions.value = false
  }, 200)
}

onMounted(() => {
  console.log('User store info on mount:', userStore.userInfo);
  fetchRequirementDetail()
  fetchParticipants()
  fetchSubmittedContents()
  fetchDocumentVersions()
  
  // 使用nextTick确保DOM已经渲染
    nextTick(() => {
      // 传入contentForm本身而不是contentForm.value
      vditor.value = initVditor('vditor-editor', contentForm);
    });
})

// 监听路由参数变化，重新获取数据
watch(() => route.params.id, (newId, oldId) => {
  if (newId !== oldId) {
    fetchRequirementDetail()
    fetchParticipants()
    fetchSubmittedContents()
    fetchDocumentVersions()
  }
})

// 显示删除确认对话框
const showRemoveConfirm = (userId, username) => {
  removeConfirmUserId.value = userId
  removeConfirmUsername.value = username
  showRemoveConfirmDialog.value = true
}

// 删除参与者
const removeParticipant = async () => {
  try {
    await api.delete(`/requirements/${route.params.id}/remove_participant/${removeConfirmUserId.value}`)
    ElMessage.success('删除参与者成功')
    showRemoveConfirmDialog.value = false
    // 刷新参与者列表
    fetchParticipants()
  } catch (error) {
    console.error('删除参与者失败:', error)
    ElMessage.error('删除参与者失败: ' + (error.response?.data?.message || error.message))
  }
}

// 显示预览对话框
const showPreviewDialog = (content) => {
  previewContent.value = content.content_text || '';
  previewContentType.value = content.content_type || 'text';
  // 通过submitted_by（用户ID）查找用户名
  const submitter = participants.value.find(p => parseInt(p.id) === parseInt(content.submitted_by)) || { username: '未知用户' };
  previewContentTitle.value = `内容预览 (${submitter.username} - ${formatDate(content.submitted_at)})`;
  previewDialogVisible.value = true;
};

// 渲染Markdown内容
const renderMarkdown = (text) => {
  return marked(text || '');
};

// 显示删除确认对话框
const deleteContent = (contentId, title) => {
  deleteContentId.value = contentId;
  deleteContentTitle.value = title || '';
  showDeleteContentDialog.value = true;
};

// 确认删除内容
const confirmDeleteContent = async () => {
  try {
    await api.delete(`/requirements/${route.params.id}/content/${deleteContentId.value}`)
    ElMessage.success('删除内容成功')
    showDeleteContentDialog.value = false
    // 刷新已提交内容列表
    await fetchSubmittedContents()
  } catch (error) {
    console.error('删除内容失败:', error)
    ElMessage.error('删除内容失败: ' + (error.response?.data?.message || error.message))
  }
};

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
  margin-right: 10px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.content-type .icon-type {
  font-size: 16px;
  color: #666;
}

.content-type .icon-preview {
  font-size: 16px;
  color: #409eff;
  cursor: pointer;
  transition: color 0.3s ease;
}

.content-type .icon-preview:hover {
  color: #66b1ff;
}

/* Font Awesome 图标样式适配 */
.content-type .el-button {
  padding: 0;
  height: auto;
}

.content-type .fa-icon {
  margin-right: 0;
}

.delete-btn {
  color: #f56c6c !important;
  margin-left: auto;
  display: inline-flex !important;
  align-items: center;
}

/* Markdown编辑器样式 */
.markdown-editor-wrapper {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
}

.editor-header {
  display: flex;
  background-color: #f5f7fa;
  border-bottom: 1px solid #dcdfe6;
  padding: 0 15px;
}

.editor-header .el-button {
  padding: 12px 15px;
  height: auto;
}

.editor-header .el-button.active {
  color: #409eff;
  background-color: #ecf5ff;
}

.editor-tips {
  margin-top: 10px;
  color: #909399;
  font-size: 12px;
  line-height: 1.5;
}

.markdown-preview {
  padding: 15px;
  min-height: 300px;
  background-color: #f5f7fa;
  overflow-y: auto;
}

.markdown-preview pre {
  background-color: #f6f8fa;
  border-radius: 3px;
  padding: 16px;
  overflow: auto;
  font-size: 14px;
  line-height: 1.5;
}

.markdown-preview code {
  background-color: #f6f8fa;
  padding: 0.2em 0.4em;
  border-radius: 3px;
  font-size: 85%;
}

.markdown-preview pre code {
  background-color: transparent;
  padding: 0;
  font-size: 14px;
}

.markdown-preview h1, .markdown-preview h2, .markdown-preview h3 {
  margin-top: 24px;
  margin-bottom: 16px;
  font-weight: 600;
  line-height: 1.25;
}

.markdown-preview h1 {
  padding-bottom: 0.3em;
  font-size: 2em;
  border-bottom: 1px solid #eaecef;
}

.markdown-preview h2 {
  padding-bottom: 0.3em;
  font-size: 1.5em;
  border-bottom: 1px solid #eaecef;
}

.markdown-preview h3 {
  font-size: 1.25em;
}

.markdown-preview p {
  margin-top: 0;
  margin-bottom: 16px;
  line-height: 1.6;
}

.markdown-preview a {
  color: #0366d6;
  text-decoration: none;
}

.markdown-preview a:hover {
  text-decoration: underline;
}

.markdown-preview ul, .markdown-preview ol {
  padding-left: 2em;
  margin-top: 0;
  margin-bottom: 16px;
}

.markdown-preview li {
  margin-bottom: 0.25em;
}

.markdown-preview img {
  max-width: 100%;
  box-sizing: content-box;
  background-color: #fff;
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

/* 邮箱候选列表样式 */
.email-suggestions {
  position: absolute;
  z-index: 1000;
  width: calc(100% - 40px);
  max-height: 200px;
  overflow-y: auto;
  background: #fff;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  margin-top: 4px;
}

.suggestion-item {
  padding: 8px 16px;
  cursor: pointer;
  transition: all 0.3s;
}

.suggestion-item:hover,
.suggestion-item.hovered {
  background-color: #f5f7fa;
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

.remove-btn {
  color: #f56c6c;
  margin-left: auto;
}

.danger-btn {
  background-color: #f56c6c;
  border-color: #f56c6c;
}

.danger-btn:hover {
  background-color: #f78989;
  border-color: #f78989;
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