<script setup>
import { ref, onMounted, watch } from "vue";
import api from "../services/api";

const operadoras = ref([]);
const page = ref(1);
const totalPages = ref(1);
const search = ref("");
const loading = ref(false); // Estado de Carregamento
const error = ref(null); // Estado de Erro

const fetchOps = async () => {
  loading.value = true;
  error.value = null;
  operadoras.value = []; // Limpa a lista anterior

  try {
    const res = await api.get("/operadoras", {
      params: { page: page.value, limit: 10, search: search.value },
    });
    operadoras.value = res.data.data;
    const meta = res.data.meta || res.data;
    totalPages.value = meta.total_pages || 1;
  } catch (e) {
    console.error(e);
    error.value =
      "Não foi possível carregar a lista de operadoras. Verifique a conexão com a API.";
  } finally {
    loading.value = false;
  }
};

// Debounce simples para a busca não chamar a API a cada letra digitada
let timeout = null;
watch(search, (newVal) => {
  clearTimeout(timeout);
  timeout = setTimeout(() => {
    page.value = 1; // Reseta para pág 1 na busca
    fetchOps();
  }, 500); // Espera 500ms
});

watch(page, fetchOps);
onMounted(fetchOps);
</script>

<template>
  <div class="container">
    <h1>Operadoras</h1>

    <div class="search-container">
      <input
        v-model="search"
        placeholder="Buscar por Razão Social ou CNPJ..."
        class="search-box"
      />
    </div>

    <div v-if="error" class="state-msg error">
      <p>{{ error }}</p>
      <button @click="fetchOps">Tentar Novamente</button>
    </div>

    <div v-else-if="loading" class="state-msg">
      <p>Carregando operadoras...</p>
    </div>

    <div v-else-if="operadoras.length > 0" class="table-responsive">
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
            <td class="truncate" :title="op.razao_social">
              {{ op.razao_social }}
            </td>
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

    <div v-else class="state-msg">
      <p>Nenhuma operadora encontrada para "{{ search }}".</p>
    </div>

    <div v-if="!loading && !error && operadoras.length > 0" class="pagination">
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
  color: #fff1ce;
}

.search-box {
  width: 100%;
  padding: 12px;
  background: #4b3c5d;
  border: 1px solid #c5a898;
  border-radius: 5px;
  color: #fff1ce;
  font-size: 1rem;
  margin-bottom: 20px;
}
.search-box::placeholder {
  color: rgba(255, 241, 206, 0.5);
}

/* Mensagens de Estado */
.state-msg {
  text-align: center;
  padding: 40px;
  background: #4b3c5d;
  border-radius: 10px;
  color: #c5a898;
  font-size: 1.1rem;
}
.state-msg.error {
  color: #ff8a80;
  border: 1px solid #ff8a80;
}
.state-msg button {
  margin-top: 10px;
  background: #e7bfa5;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
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
  table-layout: fixed;
}

th {
  background: rgba(0, 0, 0, 0.2);
  color: #c5a898;
  text-transform: uppercase;
  font-size: 0.85rem;
  padding: 15px;
  text-align: left;
}

td {
  padding: 15px;
  border-bottom: 1px solid rgba(197, 168, 152, 0.1);
  color: #fff1ce;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

tr:last-child td {
  border-bottom: none;
}
tr:hover {
  background: rgba(255, 255, 255, 0.05);
}

.truncate {
  max-width: 300px;
}
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
  background: #e7bfa5;
  color: #21203f;
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
