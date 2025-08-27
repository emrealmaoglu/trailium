<template>
  <div class="todos-page">
    <div class="page-header">
      <h1>My Todos</h1>
      <button @click="showCreateForm = true" class="btn-create">
        + New Todo
      </button>
    </div>

    <!-- Create Todo Form -->
    <div v-if="showCreateForm" class="create-form">
      <h3>Create New Todo</h3>
      <form @submit.prevent="createTodo">
        <div class="form-group">
          <label for="title">Title *</label>
          <input
            id="title"
            v-model="newTodo.title"
            type="text"
            required
            maxlength="200"
            placeholder="What needs to be done?"
            class="form-input"
          />
        </div>

        <div class="form-group">
          <label for="description">Description</label>
          <textarea
            id="description"
            v-model="newTodo.description"
            rows="3"
            maxlength="1000"
            placeholder="Additional details..."
            class="form-textarea"
          ></textarea>
        </div>

        <div class="form-group">
          <label for="priority">Priority</label>
          <select v-model="newTodo.priority" class="form-select">
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </div>

        <div class="form-group">
          <label for="due_date">Due Date</label>
          <input
            id="due_date"
            v-model="newTodo.due_date"
            type="date"
            class="form-input"
          />
        </div>

        <div class="form-actions">
          <button type="submit" :disabled="creating" class="btn-submit">
            {{ creating ? 'Creating...' : 'Create Todo' }}
          </button>
          <button type="button" @click="cancelCreate" class="btn-cancel">
            Cancel
          </button>
        </div>
      </form>
    </div>

    <!-- Todos List -->
    <div v-if="loading" class="loading">
      Loading todos...
    </div>

    <div v-else-if="todos.length === 0" class="no-todos">
      <p>No todos yet. Create your first one!</p>
    </div>

    <div v-else class="todos-list">
      <div
        v-for="todo in todos"
        :key="todo.id"
        class="todo-item"
        :class="{
          'completed': todo.is_done,
          'high-priority': todo.priority === 'high',
          'medium-priority': todo.priority === 'medium',
          'low-priority': todo.priority === 'low'
        }"
      >
        <div class="todo-header">
          <div class="todo-checkbox">
            <input
              type="checkbox"
              :checked="todo.is_done"
              @change="toggleTodo(todo.id)"
              :id="'todo-' + todo.id"
            />
            <label :for="'todo-' + todo.id"></label>
          </div>

          <div class="todo-content">
            <h3 class="todo-title">{{ todo.title }}</h3>
            <p v-if="todo.description" class="todo-description">
              {{ todo.description }}
            </p>

            <div class="todo-meta">
              <span class="priority-badge" :class="todo.priority">
                {{ todo.priority }}
              </span>
              <span v-if="todo.due_date" class="due-date">
                Due: {{ formatDate(todo.due_date) }}
              </span>
              <span class="created-date">
                Created: {{ formatDate(todo.created_at) }}
              </span>
            </div>
          </div>

          <div class="todo-actions">
            <button @click="editTodo(todo)" class="btn-edit" title="Edit">
              ✏️
            </button>
            <button @click="deleteTodo(todo.id)" class="btn-delete" title="Delete">
              🗑️
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Todo Modal -->
    <div v-if="editingTodo" class="modal-overlay" @click="cancelEdit">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Edit Todo</h3>
          <button @click="cancelEdit" class="modal-close">×</button>
        </div>

        <div class="modal-body">
          <form @submit.prevent="updateTodo">
            <div class="form-group">
              <label for="edit-title">Title *</label>
              <input
                id="edit-title"
                v-model="editingTodo.title"
                type="text"
                required
                maxlength="200"
                class="form-input"
              />
            </div>

            <div class="form-group">
              <label for="edit-description">Description</label>
              <textarea
                id="edit-description"
                v-model="editingTodo.description"
                rows="3"
                maxlength="1000"
                class="form-textarea"
              ></textarea>
            </div>

            <div class="form-group">
              <label for="edit-priority">Priority</label>
              <select v-model="editingTodo.priority" class="form-select">
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>

            <div class="form-group">
              <label for="edit-due-date">Due Date</label>
              <input
                id="edit-due-date"
                v-model="editingTodo.due_date"
                type="date"
                class="form-input"
              />
            </div>

            <div class="form-actions">
              <button type="submit" :disabled="updating" class="btn-submit">
                {{ updating ? 'Updating...' : 'Update Todo' }}
              </button>
              <button type="button" @click="cancelEdit" class="btn-cancel">
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { json } from '@/lib/http'

// State
const todos = ref([])
const loading = ref(true)
const showCreateForm = ref(false)
const creating = ref(false)
const updating = ref(false)
const editingTodo = ref(null)

// New todo form
const newTodo = ref({
  title: '',
  description: '',
  priority: 'medium',
  due_date: null
})

// Methods
async function fetchTodos() {
  try {
    loading.value = true
    const response = await json('/api/todos/items/')
    todos.value = response
  } catch (error) {
    console.error('Failed to fetch todos:', error)
  } finally {
    loading.value = false
  }
}

async function createTodo() {
  if (!newTodo.value.title.trim()) return

  try {
    creating.value = true
    const response = await json('/api/todos/items/', {
      method: 'POST',
      body: JSON.stringify(newTodo.value)
    })

    todos.value.unshift(response)
    resetForm()
    showCreateForm.value = false
  } catch (error) {
    console.error('Failed to create todo:', error)
  } finally {
    creating.value = false
  }
}

async function toggleTodo(todoId) {
  try {
    const todo = todos.value.find(t => t.id === todoId)
    if (!todo) return

    const response = await json(`/api/todos/items/${todoId}/`, {
      method: 'PATCH',
      body: JSON.stringify({ is_done: !todo.is_done })
    })

    todo.is_done = response.is_done
  } catch (error) {
    console.error('Failed to toggle todo:', error)
  }
}

async function updateTodo() {
  if (!editingTodo.value?.title.trim()) return

  try {
    updating.value = true
    const response = await json(`/api/todos/items/${editingTodo.value.id}/`, {
      method: 'PATCH',
      body: JSON.stringify(editingTodo.value)
    })

    const index = todos.value.findIndex(t => t.id === editingTodo.value.id)
    if (index !== -1) {
      todos.value[index] = response
    }

    cancelEdit()
  } catch (error) {
    console.error('Failed to update todo:', error)
  } finally {
    updating.value = false
  }
}

async function deleteTodo(todoId) {
  if (!confirm('Are you sure you want to delete this todo?')) return

  try {
    await json(`/api/todos/items/${todoId}/`, { method: 'DELETE' })
    todos.value = todos.value.filter(t => t.id !== todoId)
  } catch (error) {
    console.error('Failed to delete todo:', error)
  }
}

function editTodo(todo) {
  editingTodo.value = { ...todo }
}

function cancelEdit() {
  editingTodo.value = null
}

function cancelCreate() {
  showCreateForm.value = false
  resetForm()
}

function resetForm() {
  newTodo.value = {
    title: '',
    description: '',
    priority: 'medium',
    due_date: null
  }
}

function formatDate(dateString) {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString()
}

// Lifecycle
onMounted(() => {
  fetchTodos()
})
</script>

<style scoped>
.todos-page {
  padding: 24px;
  max-width: 800px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.page-header h1 {
  margin: 0;
  font-size: 28px;
  font-weight: 700;
  color: var(--c-text);
}

.btn-create {
  background: var(--c-accent);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-create:hover {
  background: var(--c-accent-hover);
  transform: translateY(-1px);
}

.create-form {
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 32px;
}

.create-form h3 {
  margin: 0 0 20px 0;
  color: var(--c-text);
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: var(--c-text);
}

.form-input, .form-textarea, .form-select {
  width: 100%;
  padding: 12px;
  border: 1px solid var(--c-border);
  border-radius: 8px;
  background: var(--c-surface);
  color: var(--c-text);
  font-size: 14px;
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.btn-submit, .btn-cancel {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-submit {
  background: var(--c-accent);
  color: white;
}

.btn-submit:hover:not(:disabled) {
  background: var(--c-accent-hover);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-cancel {
  background: var(--c-surface-2);
  color: var(--c-text);
  border: 1px solid var(--c-border);
}

.btn-cancel:hover {
  background: var(--c-border);
}

.loading, .no-todos {
  text-align: center;
  padding: 60px 20px;
  color: var(--c-text-muted);
}

.todos-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.todo-item {
  background: var(--c-surface);
  border: 1px solid var(--c-border);
  border-radius: 12px;
  padding: 20px;
  transition: all 0.2s ease;
}

.todo-item:hover {
  border-color: var(--c-accent);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.todo-item.completed {
  opacity: 0.7;
  background: var(--c-surface-2);
}

.todo-item.completed .todo-title {
  text-decoration: line-through;
}

.todo-header {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.todo-checkbox {
  flex-shrink: 0;
}

.todo-checkbox input[type="checkbox"] {
  display: none;
}

.todo-checkbox label {
  display: block;
  width: 24px;
  height: 24px;
  border: 2px solid var(--c-border);
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  transition: all 0.2s ease;
}

.todo-checkbox input[type="checkbox"]:checked + label {
  background: var(--c-accent);
  border-color: var(--c-accent);
}

.todo-checkbox input[type="checkbox"]:checked + label::after {
  content: '✓';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-size: 14px;
  font-weight: bold;
}

.todo-content {
  flex: 1;
  min-width: 0;
}

.todo-title {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--c-text);
}

.todo-description {
  margin: 0 0 12px 0;
  color: var(--c-text-muted);
  line-height: 1.5;
}

.todo-meta {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.priority-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
}

.priority-badge.high {
  background: #fee2e2;
  color: #dc2626;
}

.priority-badge.medium {
  background: #fef3c7;
  color: #d97706;
}

.priority-badge.low {
  background: #d1fae5;
  color: #059669;
}

.due-date, .created-date {
  font-size: 12px;
  color: var(--c-text-muted);
}

.todo-actions {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.btn-edit, .btn-delete {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.btn-edit:hover {
  background: var(--c-surface-2);
}

.btn-delete:hover {
  background: #fee2e2;
}

/* Modal styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: var(--c-surface);
  border-radius: 12px;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--c-border);
}

.modal-header h3 {
  margin: 0;
  color: var(--c-text);
}

.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: var(--c-text-muted);
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
}

.modal-close:hover {
  background: var(--c-surface-2);
}

.modal-body {
  padding: 24px;
}

/* Priority colors for todo items */
.todo-item.high-priority {
  border-left: 4px solid #dc2626;
}

.todo-item.medium-priority {
  border-left: 4px solid #d97706;
}

.todo-item.low-priority {
  border-left: 4px solid #059669;
}
</style>
