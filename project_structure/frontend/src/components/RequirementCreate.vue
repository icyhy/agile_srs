<template>
  <div class="requirement-create">
    <el-form 
      :model="form" 
      :rules="rules" 
      ref="formRef" 
      label-width="100px"
    >
      <el-form-item label="需求标题" prop="title">
        <el-input 
          v-model="form.title" 
          placeholder="请输入需求标题"
          clearable
        />
      </el-form-item>
      
      <el-form-item label="需求描述" prop="description">
        <el-input 
          v-model="form.description" 
          type="textarea" 
          :rows="4"
          placeholder="请输入需求描述"
        />
      </el-form-item>
      
      <el-form-item>
        <el-button 
          type="primary" 
          @click="handleSubmit" 
          :loading="loading"
        >
          创建需求
        </el-button>
        <el-button @click="handleCancel">
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
.requirement-create {
  max-width: 600px;
  margin: 0 auto;
}
</style>