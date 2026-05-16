<template>
  <div class="crud-view">
    <h1>{{ title }}</h1>

    <!-- Actions -->
    <div class="actions">
      <el-button type="primary" @click="showAddDialog = true">{{ t('common.add') }}</el-button>
      <el-input v-model="searchKeyword" placeholder="Search..." style="width: 300px; margin-left: 20px" />
    </div>

    <!-- Table -->
    <el-table :data="filteredData" style="width: 100%; margin-top: 20px" v-loading="loading">
      <el-table-column v-for="col in columns" :key="col.prop" :prop="col.prop" :label="col.label" />
      <el-table-column label="Actions" width="180">
        <template #default="{ row }">
          <el-button size="small" @click="editItem(row)">{{ t('common.edit') }}</el-button>
          <el-button size="small" type="danger" @click="deleteItem(row)">{{ t('common.delete') }}</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- Add/Edit Dialog -->
    <el-dialog v-model="showAddDialog" :title="editingItem ? 'Edit' : 'Add'" width="600px">
      <el-form :model="formData" label-width="120px">
        <el-form-item v-for="col in formColumns" :key="col.prop" :label="col.label">
          <el-input v-model="formData[col.prop!]" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" @click="saveItem">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps<{
  title: string
  columns: Array<{ prop: string; label: string }>
  formColumns?: Array<{ prop: string; label: string }>
  dataLoader: () => Promise<any[]>
}>()

const data = ref<any[]>([])
const loading = ref(false)
const searchKeyword = ref('')
const showAddDialog = ref(false)
const editingItem = ref<any>(null)
const formData = ref<any>({})

const filteredData = computed(() => {
  if (!searchKeyword.value) return data.value
  return data.value.filter(item =>
    Object.values(item).some(v => String(v).toLowerCase().includes(searchKeyword.value.toLowerCase()))
  )
})

const loadData = async () => {
  loading.value = true
  try {
    data.value = await props.dataLoader()
  } catch (error) {
    console.error('Failed to load data:', error)
  } finally {
    loading.value = false
  }
}

const editItem = (row: any) => {
  editingItem.value = row
  formData.value = { ...row }
  showAddDialog.value = true
}

const deleteItem = (row: any) => {
  console.log('Delete:', row)
}

const saveItem = () => {
  console.log('Save:', formData.value)
  showAddDialog.value = false
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.crud-view {
  max-width: 1200px;
}

.actions {
  display: flex;
  gap: 10px;
}
</style>