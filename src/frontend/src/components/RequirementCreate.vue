<template>
  <div class="requirement-create">
    <el-form 
      :model="form" 
      :rules="rules" 
      ref="formRef" 
      label-width="100px"
      class="create-form"
      size="large"
    >
      <el-form-item label="需求标题" prop="title">
        <el-input 
          v-model="form.title" 
          placeholder="请输入需求标题"
          clearable
          size="large"
          class="large-input"
        />
      </el-form-item>
      
      <el-form-item label="需求描述" prop="description">
        <el-input 
          v-model="form.description" 
          type="textarea" 
          :rows="8"
          placeholder="请输入需求描述"
          resize="vertical"
          class="large-textarea"
        />
      </el-form-item>
      
      <el-form-item>
        <el-button 
          type="primary" 
          @click="handleSubmit" 
          :loading="loading"
          size="large"
        >
          创建需求
        </el-button>
        <el-button 
          @click="handleCancel"
          size="large"
        >
          取消
        </el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import api from '../utils/api'

export default {
  name: 'RequirementCreate',
  emits: ['created', 'cancel'],
  setup(props, { emit }) {
    const formRef = ref()
    
    const form = reactive({
      title: '',
      description: ''
    })
    
    const loading = ref(false)
    
    const rules = {
      title: [
        { required: true, message: '请输入需求标题', trigger: 'blur' },
        { min: 1, max: 100, message: '标题长度为1-100个字符', trigger: 'blur' }
      ],
      description: [
        { max: 500, message: '描述长度最多500个字符', trigger: 'blur' }
      ]
    }
    
    const handleSubmit = async () => {
      try {
        await formRef.value.validate()
        
        loading.value = true
        
        const response = await api.post('/requirements/create', {
          title: form.title,
          description: form.description
        })
        
        emit('created', response.data.requirement)
        
        // 重置表单
        form.title = ''
        form.description = ''
      } catch (error) {
        console.error('创建需求失败:', error)
        alert('创建需求失败')
      } finally {
        loading.value = false
      }
    }
    
    const handleCancel = () => {
      emit('cancel')
    }
    
    return {
      formRef,
      form,
      loading,
      rules,
      handleSubmit,
      handleCancel
    }
  }
}
</script>

<style scoped>
/* 确保与列表页面标题栏高度一致 */
.requirement-create {
  width: 100%;
  margin: 0;
  padding: 0;
}

/* 表单样式优化 */
.create-form {
  width: 100%;
}

.create-form .el-form-item {
  margin-bottom: 24px;
}

.create-form .el-form-item__label {
  font-weight: 500;
  font-size: 14px;
  padding: 12px 12px 12px 0;
}

/* 输入框样式优化 - 宽度最大化 */
.create-form .el-input,
.create-form .el-input__wrapper {
  width: 100% !important;
  max-width: none !important;
}

.large-input {
  height: 50px;
  font-size: 14px;
  --el-input-height: 50px;
}

.large-textarea {
  font-size: 14px;
  min-height: 160px;
  width: 100% !important;
  max-width: none !important;
}

/* 按钮样式优化 */
.create-form .el-button {
  margin-right: 12px;
}
</style>