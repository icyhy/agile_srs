<template>
  <div class="login-container">
    <div class="login-left">
      <div class="login-left-content">
        <h1>用户需求收集系统</h1>
        <p>欢迎使用用户需求收集系统，高效收集和管理用户需求...</p>
      </div>
    </div>
    <div class="login-right">
      <div class="login-form">
        <h2>欢迎回来</h2>
        <div class="third-party-login">
          <button class="social-btn facebook"><FontAwesomeIcon icon="fa-brands fa-facebook-f" /></button>
          <button class="social-btn twitter"><FontAwesomeIcon icon="fa-brands fa-twitter" /></button>
          <button class="social-btn linkedin"><FontAwesomeIcon icon="fa-brands fa-linkedin-in" /></button>
        </div>
        <div class="divider">
          <span>使用电子邮箱登录</span>
        </div>
        <el-form :model="loginForm" :rules="rules" ref="loginFormRef">
        <el-form-item prop="email">
          <el-input 
            v-model="loginForm.email" 
            placeholder="邮箱" 
            type="email"
            clearable
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input 
            v-model="loginForm.password" 
            placeholder="密码" 
            type="password"
            show-password
          />
        </el-form-item>
        <div class="remember-password">
          <el-checkbox v-model="rememberMe">记住我</el-checkbox>
          <a href="#" class="forgot-password">忘记密码?</a>
        </div>
        <el-form-item>
          <el-button 
            type="primary" 
            @click="handleLogin" 
            :loading="loading"
            style="width: 100%"
          >
            登录
          </el-button>
        </el-form-item>
        <p class="register-link">
          还没有账号？<a href="#" @click="goToRegister">立即注册</a>
        </p>
      </el-form>
    </div>
  </div>
</div>
</template>

<script>
import { ref, onMounted } from 'vue'
// Font Awesome已在main.js中全局注册
import { useRouter } from 'vue-router'
import { useUserStore } from '../store'
import api from '../utils/api'

export default {
  name: 'Login',
  setup() {
    const router = useRouter()
    const userStore = useUserStore()
    
    const loginForm = ref({
      email: '',
      password: ''
    })
    
    const rememberMe = ref(false)
    
    const loading = ref(false)
    
    const rules = {
      email: [
        { required: true, message: '请输入邮箱', trigger: 'blur' },
        { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
      ],
      password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 6, message: '密码长度至少6位', trigger: 'blur' }
      ]
    }
    
    const handleLogin = async () => {
      loading.value = true
      try {
        const response = await api.post('/users/login', loginForm.value)
        const { access_token, user } = response.data
        
        userStore.setToken(access_token)
        userStore.setUser(user)
        
        // 添加调试日志
        console.log('User info after login:', userStore.userInfo);
        
        router.push('/dashboard')
      } catch (error) {
        console.error('Login failed:', error)
        alert('登录失败，请检查邮箱和密码')
      } finally {
        loading.value = false
      }
    }
    
    const goToRegister = () => {
      router.push('/register')
    }
    
    // 组件挂载时，检查是否有保存的邮箱
    onMounted(() => {
      const savedEmail = localStorage.getItem('rememberedEmail')
      if (savedEmail) {
        loginForm.value.email = savedEmail
        rememberMe.value = true
      }
    })
    
    // 登录成功后的处理增强
    const originalHandleLogin = handleLogin
    const enhancedHandleLogin = async () => {
      await originalHandleLogin()
      
      // 如果登录成功且勾选了记住用户名，则保存邮箱
      if (userStore.token && rememberMe.value) {
        localStorage.setItem('rememberedEmail', loginForm.value.email)
      } else if (!rememberMe.value) {
        // 如果未勾选，则清除保存的邮箱
        localStorage.removeItem('rememberedEmail')
      }
    }
    
    return {
      loginForm,
      loading,
      rules,
      handleLogin: enhancedHandleLogin,
      goToRegister,
      rememberMe
    }
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

.login-left {
  flex: 1;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 0 50px;
  position: relative;
  overflow: hidden;
}

.login-left::before {
  content: '';
  position: absolute;
  width: 200px;
  height: 200px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  top: -50px;
  left: -50px;
}

.login-left::after {
  content: '';
  position: absolute;
  width: 150px;
  height: 150px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.15);
  bottom: 50px;
  right: 100px;
}

.login-left-content {
  z-index: 1;
  text-align: center;
}

.login-left h1 {
  font-size: 2.5rem;
  margin-bottom: 20px;
  font-weight: bold;
}

.login-left p {
  font-size: 1.1rem;
  opacity: 0.9;
  max-width: 300px;
}

.login-right {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: white;
  padding: 0 50px;
}

.login-form {
  width: 100%;
  max-width: 400px;
  padding: 40px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 5px 25px rgba(0, 0, 0, 0.05);
}

.login-form h2 {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
  font-size: 1.8rem;
  font-weight: 600;
}

.third-party-login {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-bottom: 25px;
}

.social-btn {
  width: 45px;
  height: 45px;
  border-radius: 50%;
  border: none;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 18px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.facebook {
  background-color: #3b5998;
  color: white;
}

.twitter {
  background-color: #1da1f2;
  color: white;
}

.linkedin {
  background-color: #0077b5;
  color: white;
}

.social-btn:hover {
  transform: translateY(-3px);
  opacity: 0.9;
}

.divider {
  display: flex;
  align-items: center;
  margin-bottom: 25px;
}

.divider::before, .divider::after {
  content: '';
  flex-grow: 1;
  height: 1px;
  background-color: #e0e0e0;
}

.divider span {
  padding: 0 15px;
  color: #9e9e9e;
  font-size: 0.9rem;
}

.remember-password {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  font-size: 0.95rem;
}

.forgot-password {
  color: #667eea;
  text-decoration: none;
  transition: color 0.3s ease;
}

.forgot-password:hover {
  color: #764ba2;
  text-decoration: underline;
}

.el-button--primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  height: 45px;
  font-size: 1rem;
  font-weight: 500;
  transition: all 0.3s ease;
}

.el-button--primary:hover {
  opacity: 0.9;
  transform: translateY(-2px);
}

.register-link {
  text-align: center;
  margin-top: 25px;
  font-size: 0.95rem;
  color: #333;
}

.register-link a {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
}

.register-link a:hover {
  color: #764ba2;
  text-decoration: underline;
}

/* 调整表单元素样式 */
.el-input__wrapper {
  border-radius: 8px;
  height: 45px;
}

.el-checkbox__label {
  color: #333;
}
</style>