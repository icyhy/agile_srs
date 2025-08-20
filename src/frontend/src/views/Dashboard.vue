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
      requirementStore.setCurrentRequirement(requirement)
      router.push(`/requirement/${requirement.id}`)
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
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background-color: #f0f2f5;
}

.header {
  background-color: #409eff;
  color: white;
  padding: 0;
  height: 64px;
  box-shadow: 0 2px 8px 0 rgba(0, 0, 0, 0.15);
  z-index: 10;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  height: 100%;
}

/* 系统标题样式优化 */
.header-content h2 {
  font-size: 20px;
  font-weight: 600;
  margin: 0;
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.header-content h2:hover {
  transform: translateX(5px);
}

.header-content h2::before {
  content: "🎯";
  margin-right: 8px;
  font-size: 24px;
}

/* 用户信息区域样式优化 */
.user-info {
  cursor: pointer;
  padding: 8px 16px;
  border-radius: 20px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  background-color: rgba(255, 255, 255, 0.1);
}

.user-info:hover {
  background-color: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
}

.user-info .el-dropdown-link {
  color: white;
  font-weight: 500;
  display: flex;
  align-items: center;
}

/* 左侧导航栏样式优化 */
.sidebar {
  background-color: #ffffff;
  height: 100%;
  overflow-y: auto;
  border-right: 1px solid #e4e7ed;
  box-shadow: 2px 0 8px 0 rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.sidebar:hover {
  box-shadow: 2px 0 12px 0 rgba(0, 0, 0, 0.1);
}

.sidebar-menu {
  border-right: none;
  height: 100%;
  overflow: hidden;
}

.sidebar-menu .el-menu-item {
  height: 60px;
  line-height: 60px;
  font-size: 14px;
  transition: all 0.3s ease;
}

.sidebar-menu .el-menu-item:hover {
  background-color: #f0f7ff;
  color: #409eff;
}

.sidebar-menu .el-menu-item.is-active {
  background-color: #e6f7ff;
  color: #409eff;
  border-right: 3px solid #409eff;
}

.sidebar-menu .el-menu-item .el-icon {
  font-size: 18px;
  margin-right: 12px;
}

/* 右侧内容区域样式优化 */
.main-content {
  padding: 20px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background-color: #f0f2f5;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid #e4e7ed;
}

.content-header h3 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  color: #303133;
}

.content-body {
  background: white;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
}

.content-body:hover {
  box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.15);
}
</style>