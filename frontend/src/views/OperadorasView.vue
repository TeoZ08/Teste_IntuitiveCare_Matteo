<script setup>
import { ref, onMounted, watch } from "vue";
import api from "../services/api";

const operadoras = ref([]);
const page = ref(1);
const totalPages = ref(1);
const search = ref("");

const fetchOps = async () => {
  try {
    const res = await api.get("/operadoras", {
      params: { page: page.value, limit: 10, search: search.value },
    });
    operadoras.value = res.data.data;
    const meta = res.data.meta || res.data;
    totalPages.value = meta.total_pages || 1;
  } catch (e) {
    console.error(e);
  }
};

watch([page, search], fetchOps);
onMounted(fetchOps);
</script>

<template>
  <div class="container">
    <h1>Operadoras</h1>
    <input
      v-model.lazy="search"
      placeholder="Buscar por Razão Social ou CNPJ..."
      class="search-box"
    />

    <div class="table-responsive">
      <table>
        <thead>
          <tr>
            <th>Razão Social</th>
            <th>CNPJ</th>
            <th>UF</th>
            <th>Ação</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="op in operadoras" :key="op.reg_ans">
            <td>{{ op.razao_social }}</td>
            <td>{{ op.cnpj }}</td>
            <td>{{ op.uf }}</td>
            <td>
              <router-link :to="`/operadoras/${op.reg_ans}`" class="btn-link">
                Detalhes
              </router-link>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="pagination">
      <button :disabled="page <= 1" @click="page--">Anterior</button>
      <span>Pág {{ page }} de {{ totalPages }}</span>
      <button :disabled="page >= totalPages" @click="page++">Próxima</button>
    </div>
  </div>
</template>

<style scoped>
.container {
  padding: 20px 40px;
  max-width: 1200px;
  margin: 0 auto;
}
h1 {
  font-weight: 300;
  margin-bottom: 20px;
}

/* Input de Busca */
.search-box {
  width: 100%;
  padding: 12px;
  background: #4b3c5d; /* Color 5 */
  border: 1px solid #c5a898; /* Color 4 */
  border-radius: 5px;
  color: #fff1ce;
  font-size: 1rem;
  margin-bottom: 20px;
}
.search-box::placeholder {
  color: rgba(255, 241, 206, 0.5);
}

/* Tabela */
.table-responsive {
  background: #4b3c5d;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}
table {
  width: 100%;
  border-collapse: collapse;
}

th {
  background: rgba(0, 0, 0, 0.2);
  color: #c5a898; /* Color 4 */
  text-transform: uppercase;
  font-size: 0.85rem;
  padding: 15px;
  text-align: left;
}

td {
  padding: 15px;
  border-bottom: 1px solid rgba(197, 168, 152, 0.1);
  color: #fff1ce;
}

tr:last-child td {
  border-bottom: none;
}
tr:hover {
  background: rgba(255, 255, 255, 0.05);
}

/* Botões */
.btn-link {
  color: #e7bfa5;
  font-weight: bold;
  font-size: 0.9rem;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  gap: 15px;
  align-items: center;
}

button {
  background: #e7bfa5; /* Color 3 */
  color: #21203f; /* Color 1 (Texto escuro no botão claro) */
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  transition: opacity 0.3s;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
button:hover:not(:disabled) {
  opacity: 0.9;
}
</style>
