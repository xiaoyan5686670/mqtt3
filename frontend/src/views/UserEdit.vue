<template>
  <div class="user-edit">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>
        <i class="fas fa-user-edit me-2"></i>
        {{ isEdit ? '编辑用户' : '添加用户' }}
      </h2>
      <router-link to="/users" class="btn btn-secondary">
        <i class="fas fa-arrow-left me-2"></i>返回
      </router-link>
    </div>

    <div class="card">
      <div class="card-body">
        <form @submit.prevent="handleSubmit">
          <div class="mb-3">
            <label for="username" class="form-label">用户名 *</label>
            <input
              type="text"
              class="form-control"
              id="username"
              v-model="form.username"
              required
              :disabled="isEdit"
            />
            <small class="text-muted">编辑时用户名不可修改</small>
          </div>

          <div class="mb-3">
            <label for="email" class="form-label">邮箱</label>
            <input
              type="email"
              class="form-control"
              id="email"
              v-model="form.email"
            />
          </div>

          <div class="mb-3">
            <label for="password" class="form-label">
              {{ isEdit ? '新密码（留空则不修改）' : '密码 *' }}
            </label>
            <input
              type="password"
              class="form-control"
              id="password"
              v-model="form.password"
              :required="!isEdit"
            />
          </div>

          <div class="mb-3">
            <div class="form-check">
              <input
                class="form-check-input"
                type="checkbox"
                id="is_active"
                v-model="form.is_active"
              />
              <label class="form-check-label" for="is_active">
                启用
              </label>
            </div>
          </div>

          <div class="mb-3">
            <div class="form-check">
              <input
                class="form-check-input"
                type="checkbox"
                id="is_admin"
                v-model="form.is_admin"
              />
              <label class="form-check-label" for="is_admin">
                管理员权限
              </label>
            </div>
          </div>

          <div v-if="error" class="alert alert-danger">
            {{ error }}
          </div>

          <div class="d-flex gap-2">
            <button type="submit" class="btn btn-primary" :disabled="loading">
              <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
              {{ isEdit ? '更新' : '创建' }}
            </button>
            <router-link to="/users" class="btn btn-secondary">取消</router-link>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRoute, useRouter } from 'vue-router'

export default {
  name: 'UserEdit',
  props: {
    id: {
      type: String,
      default: null
    }
  },
  setup(props) {
    const route = useRoute()
    const router = useRouter()
    const loading = ref(false)
    const error = ref('')
    const userId = props.id || route.params.id
    const isEdit = !!userId

    const form = ref({
      username: '',
      email: '',
      password: '',
      is_active: true,
      is_admin: false
    })

    const fetchUser = async () => {
      if (!isEdit) return

      try {
        const response = await axios.get(`/api/users/${userId}/`)
        const user = response.data
        form.value = {
          username: user.username,
          email: user.email || '',
          password: '',
          is_active: user.is_active,
          is_admin: user.is_admin
        }
      } catch (err) {
        error.value = err.response?.data?.detail || err.message || '获取用户信息失败'
      }
    }

    const handleSubmit = async () => {
      loading.value = true
      error.value = ''

      try {
        const data = {
          username: form.value.username,
          email: form.value.email || null,
          is_active: form.value.is_active,
          is_admin: form.value.is_admin
        }

        if (form.value.password) {
          data.password = form.value.password
        }

        if (isEdit) {
          await axios.put(`/api/users/${userId}/`, data)
        } else {
          await axios.post('/api/users/', data)
        }

        router.push('/users')
      } catch (err) {
        error.value = err.response?.data?.detail || err.message || '保存失败'
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      if (isEdit) {
        fetchUser()
      }
    })

    return {
      form,
      loading,
      error,
      isEdit,
      handleSubmit
    }
  }
}
</script>
