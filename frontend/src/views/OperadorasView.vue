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
    // Ajuste aqui se sua API retorna 'meta' ou direto na raiz
    const meta = res.data.meta || res.data;
    totalPages.value = meta.total_pages || 1;
  } catch (e) {
    console.error(e);
  }
};

watch([page, search], fetchOps); // Recarrega se mudar página ou busca
onMounted(fetchOps);
</script>

<template>
  <div class="container">
    <h1>Operadoras</h1>
    <input
      v-model.lazy="search"
      placeholder="Buscar operadora..."
      class="search-box"
    />

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
            <router-link :to="`/operadoras/${op.reg_ans}`"
              >Detalhes</router-link
            >
          </td>
        </tr>
      </tbody>
    </table>

    <div class="pagination">
      <button :disabled="page <= 1" @click="page--">Anterior</button>
      <span>Pág {{ page }}</span>
      <button :disabled="page >= totalPages" @click="page++">Próxima</button>
    </div>
  </div>
</template>

<style scoped>
.container {
  padding: 20px;
}
.search-box {
  padding: 8px;
  width: 100%;
  margin-bottom: 15px;
}
table {
  width: 100%;
  border-collapse: collapse;
}
th,
td {
  padding: 10px;
  border-bottom: 1px solid #ddd;
  text-align: left;
}
.pagination {
  margin-top: 15px;
  display: flex;
  gap: 10px;
}
</style>
