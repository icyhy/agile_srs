<template>
  <div class="dashboard">
    <el-container>
      <el-header class="header">
        <div class="header-content">
          <h2>需求调研管理系统</h2>
          <div class="user-info">
            <el-dropdown @command="handleUserCommand">
              <span class="el-dropdown-link">
                {{ userStore.userInfo?.username || '用户' }}
                <el-icon class="el-icon--right">
                  <arrow-down />
                </el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">个人资料</el-dropdown-item>
                  <el-dropdown-item command="logout">退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </el-header>
      
      <el-container>
        <el-aside width="200px" class="sidebar">
          <el-menu
            default-active="1"
            class="sidebar-menu"
            @select="handleMenuSelect"
          >
            <el-menu-item index="1">
              <el-icon><document /></el-icon>
              <span>我的需求</span>
            </el-menu-item>
            <el-menu-item index="2">
              <el-icon><plus /></el-icon>
              <span>创建需求</span>
            </el-menu-item>
          </el-menu>
        </el-aside>
        
        <el-main class="main-content">
          <div class="content-header">
            <h3>{{ currentView === 'list' ? '我的需求任务' : '创建新需求' }}</h3>
            <el-button 
              v-if="currentView === 'list'" 
              type="primary" 
              @click="switchToCreate"
            >
              <el-icon><plus /></el-icon>
              创建需求
            </el-button>
          </div>
          
          <div class="content-body">
            <RequirementList 
              v-if="currentView === 'list'" 
              @edit="handleEditRequirement"
              @view="handleViewRequirement"
              ref="requirementListRef"
            />
            <RequirementCreate 
              v-if="currentView === 'create'" 
              @created="handleRequirementCreated"
              @cancel="switchToList"
            />
          </div>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore, useRequirementStore } from '../store'
import api from '../utils/api'
import RequirementList from '../components/RequirementList.vue'
import RequirementCreate from '../components/RequirementCreate.vue'
import { Document, Plus, ArrowDown } from '@element-plus/icons-vue'

export default {
  name: 'Dashboard',
  components: {
    RequirementList,
    RequirementCreate,
    Document,
    Plus,
    ArrowDown
  },
  setup() {
    const router = useRouter()
    const userStore = useUserStore()
    const requirementStore = useRequirementStore()
    
    const currentView = ref('list') // 'list' or 'create'
    const requirementListRef = ref(null)
    
    const handleUserCommand = (command) => {
      if (command === 'logout') {
        userStore.logout()
        router.push('/login')
      } else if (command === 'profile') {
        // TODO: 显示个人资料
        console.log('显示个人资料')
      }
    }
    
    const handleMenuSelect = (index) => {
      if (index === '1') {
        currentView.value = 'list'
      } else if (index === '2') {
        currentView.value = 'create'
      }
    }
    
    const switchToCreate = () => {
      currentView.value = 'create'
    }
    
    const switchToList = () => {
      currentView.value = 'list'
    }
    
    const handleRequirementCreated = (requirement) => {
      requirementStore.addRequirement(requirement)
      switchToList()
    }
    
    const handleEditRequirement = (requirement) => {
      // TODO: 编辑需求
      console.log('编辑需求:', requirement)
    }
    
    const handleViewRequirement = (requirement) => {
      requirementStore.setCurrentRequirement(requirement)
      router.push(`/requirement/${requirement.id}`)
    }
    
    // 移除重复的需求列表加载逻辑，由RequirementList组件负责加载
    // onMounted(async () => {
    //   try {
    //     // 调用API获取需求列表
    //     const response = await api.get('/requirements/list')
    //     requirementStore.setRequirements(response.data.requirements)
    //   } catch (error) {
    //     console.error('获取需求列表失败:', error)
    //   }
    // })
    
    // 监听视图变化，切换到列表时刷新数据
    watch(currentView, (newValue) => {
      if (newValue === 'list' && requirementListRef.value) {
        requirementListRef.value.fetchRequirements()
      }
    })
    
    return {
      userStore,
      currentView,
      handleUserCommand,
      handleMenuSelect,
      switchToCreate,
      switchToList,
      handleRequirementCreated,
      handleEditRequirement,
      handleViewRequirement
    }
  }
}
</script>

<style scoped>
.dashboard {
  height: 100vh;
}

.header {
  background-color: #409eff;
  color: white;
  padding: 0;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  height: 100%;
}

.user-info {
  cursor: pointer;
}

.sidebar {
  background-color: #f5f5f5;
}

.sidebar-menu {
  border-right: none;
}

.main-content {
  padding: 20px;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.content-body {
  background: white;
  padding: 20px;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}
</style>