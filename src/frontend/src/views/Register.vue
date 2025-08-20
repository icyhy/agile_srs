<template>
  <div class="register-container">
    <div class="register-form">
      <h2>注册账户</h2>
      <el-form :model="registerForm" :rules="rules" ref="formRef">
        <el-form-item prop="username">
          <el-input 
            v-model="registerForm.username" 
            placeholder="用户名" 
            clearable
          />
        </el-form-item>
        <el-form-item prop="email">
          <el-input 
            v-model="registerForm.email" 
            placeholder="邮箱" 
            type="email"
            clearable
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input 
            v-model="registerForm.password" 
            placeholder="密码" 
            type="password"
            show-password
          />
        </el-form-item>
        <el-form-item prop="confirmPassword">
          <el-input 
            v-model="registerForm.confirmPassword" 
            placeholder="确认密码" 
            type="password"
            show-password
          />
        </el-form-item>
        <el-form-item>
          <el-button 
            type="primary" 
            @click="handleRegister" 
            :loading="loading"
            style="width: 100%"
          >
            注册
          </el-button>
        </el-form-item>
        <el-form-item>
          <el-button @click="goToLogin" style="width: 100%">
            已有账户，前往登录
          </el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

export default {
  name: 'Register',
  setup() {
    const router = useRouter()
    
    const registerForm = reactive({
      username: '',
      email: '',
      password: '',
      confirmPassword: ''
    })
    
    const formRef = ref(null)
    
    const loading = ref(false)
    
    const validatePassword = (rule, value, callback) => {
      if (value !== registerForm.password) {
        callback(new Error('两次输入的密码不一致'))
      } else {
        callback()
      }
    }
    
    const rules = {
      username: [
        { required: true, message: '请输入用户名', trigger: 'blur' },
        { min: 3, max: 20, message: '用户名长度为3-20个字符', trigger: 'blur' }
      ],
      email: [
        { required: true, message: '请输入邮箱', trigger: 'blur' },
        { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
      ],
      password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 6, message: '密码长度至少6位', trigger: 'blur' }
      ],
      confirmPassword: [
        { required: true, message: '请确认密码', trigger: 'blur' },
        { validator: validatePassword, trigger: 'blur' }
      ]
    }
    
    const handleRegister = async () => {
      loading.value = true
      try {
        const { username, email, password } = registerForm
        await axios.post('/api/users/register', { username, email, password })
        
        alert('注册成功，请登录')
        router.push('/login')
      } catch (error) {
        console.error('Registration failed:', error)
        alert('注册失败，请稍后重试')
      } finally {
        loading.value = false
      }
    }
    
    const goToLogin = () => {
      router.push('/login')
    }
    
    return {
      registerForm,
      formRef,
      loading,
      rules,
      handleRegister,
      goToLogin
    }
  }
}
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f5f5;
}

.register-form {
  width: 100%;
  max-width: 400px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.register-form h2 {
  text-align: center;
  margin-bottom: 20px;
  color: #333;
}
</style>