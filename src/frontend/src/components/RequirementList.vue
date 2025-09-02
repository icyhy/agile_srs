<template>
  <div class="requirement-list">
    <el-table :data="requirements" style="width: 100%" v-loading="loading">
      <el-table-column prop="title" label="需求标题" />
      <el-table-column prop="description" label="描述" />
      <el-table-column prop="created_at" label="创建时间">
        <template #default="scope">
          {{ formatDate(scope.row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" />
      <el-table-column label="操作" width="100">
        <template #default="scope">
          <el-button 
            size="small" 
            @click="handleView(scope.row)"
          >
            查看
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <div class="empty-placeholder" v-if="!loading && requirements.length === 0">
      <el-empty description="暂无需求任务" />
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useRequirementStore } from '../store'
import api from '../utils/api'

export default {
  name: 'RequirementList',
  emits: ['view'],
  setup(props, { emit }) {
    const requirementStore = useRequirementStore()
    
    const loading = ref(false)
    
    const formatDate = (dateString) => {
      const date = new Date(dateString)
      return date.toLocaleDateString('zh-CN')
    }
    
    // 移除了handleEdit函数
    
    const handleView = (requirement) => {
      emit('view', requirement)
    }
    
    // 获取需求列表
    const fetchRequirements = async () => {
      loading.value = true
      try {
        const response = await api.get('/requirements/list')
        requirementStore.setRequirements(response.data.requirements)
      } catch (error) {
        console.error('获取需求列表失败:', error)
        alert('获取需求列表失败')
      } finally {
        loading.value = false
      }
    }
    
    onMounted(() => {
      fetchRequirements()
    })
    
    // 使用storeToRefs保持响应式
    const { requirements } = storeToRefs(requirementStore)
    
    // 暴露刷新方法
    return {
      requirements,
      loading,
      formatDate,
      handleView,
      fetchRequirements
    }
  }
}
</script>

<style scoped>
.requirement-list {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.el-table {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.el-table__body-wrapper {
  flex: 1;
  overflow-y: auto;
}

.empty-placeholder {
  display: flex;
  justify-content: center;
  align-items: center;
  flex: 1;
}
</style>