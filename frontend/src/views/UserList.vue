<template>
  <div class="user-list">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>
        <i class="fas fa-users me-2"></i>
        用户管理
      </h2>
      <router-link to="/users/new" class="btn btn-primary">
        <i class="fas fa-plus me-2"></i>添加用户
      </router-link>
    </div>

    <div class="card">
      <div class="card-body">
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">加载中...</span>
          </div>
        </div>

        <div v-else-if="error" class="alert alert-danger">
          {{ error }}
        </div>

        <div v-else>
          <table class="table table-hover">
            <thead>
              <tr>
                <th>ID</th>
                <th>用户名</th>
                <th>邮箱</th>
                <th>角色</th>
                <th>状态</th>
                <th>创建时间</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in users" :key="user.id">
                <td>{{ user.id }}</td>
                <td>{{ user.username }}</td>
                <td>{{ user.email || '-' }}</td>
                <td>
                  <span class="badge" :class="user.is_admin ? 'bg-warning' : 'bg-secondary'">
                    {{ user.is_admin ? '管理员' : '普通用户' }}
                  </span>
                </td>
                <td>
                  <span class="badge" :class="user.is_active ? 'bg-success' : 'bg-danger'">
                    {{ user.is_active ? '启用' : '禁用' }}
                  </span>
                </td>
                <td>{{ formatDate(user.created_at) }}</td>
                <td>
                  <router-link 
                    :to="`/users/${user.id}/edit`" 
                    class="btn btn-sm btn-outline-primary me-2"
                  >
                    <i class="fas fa-edit"></i> 编辑
                  </router-link>
                  <button 
                    class="btn btn-sm btn-outline-danger"
                    @click="handleDelete(user)"
                    :disabled="user.id === currentUserId"
                  >
                    <i class="fas fa-trash"></i> 删除
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'

export default {
  name: 'UserList',
  setup() {
    const users = ref([])
    const loading = ref(false)
    const error = ref('')
    const authStore = useAuthStore()
    const router = useRouter()
    const currentUserId = ref(null)

    const fetchUsers = async () => {
      loading.value = true
      error.value = ''
      try {
        // 使用带尾部斜杠的路径，避免 FastAPI 重定向导致 token 丢失
        const response = await axios.get('/api/users/')
        users.value = response.data
        // 获取当前用户ID
        if (authStore.user) {
          currentUserId.value = authStore.user.id
        }
      } catch (err) {
        const status = err.response?.status
        if (status === 401) {
          // 认证失败，跳转到登录页
          authStore.logout()
          router.push('/login')
          return
        } else if (status === 403) {
          // 权限不足，显示错误信息但不退出
          error.value = '权限不足，只有管理员可以访问用户管理'
        } else {
          error.value = err.response?.data?.detail || err.message || '获取用户列表失败'
        }
      } finally {
        loading.value = false
      }
    }

    const handleDelete = async (user) => {
      if (!confirm(`确定要删除用户 "${user.username}" 吗？`)) {
        return
      }

      try {
        await axios.delete(`/api/users/${user.id}/`)
        await fetchUsers()
      } catch (err) {
        const status = err.response?.status
        if (status === 401) {
          authStore.logout()
          router.push('/login')
        } else {
          alert(err.response?.data?.detail || err.message || '删除用户失败')
        }
      }
    }

    const formatDate = (dateString) => {
      if (!dateString) return '-'
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN')
    }

    onMounted(() => {
      fetchUsers()
    })

    return {
      users,
      loading,
      error,
      currentUserId,
      fetchUsers,
      handleDelete,
      formatDate
    }
  }
}
</script>
