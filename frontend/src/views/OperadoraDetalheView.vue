<script setup>
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import api from "../services/api";

const route = useRoute();
const op = ref(null);
const despesas = ref([]);

onMounted(async () => {
  const id = route.params.id;
  try {
    const [resOp, resDesp] = await Promise.all([
      api.get(`/operadoras/${id}`),
      api.get(`/operadoras/${id}/despesas`),
    ]);
    op.value = resOp.data;
    despesas.value = resDesp.data;
  } catch (e) {
    console.error(e);
  }
});
</script>

<template>
  <div class="container" v-if="op">
    <div class="header-card">
      <h1>{{ op.razao_social }}</h1>
      <div class="info-grid">
        <p><strong>CNPJ:</strong> {{ op.cnpj }}</p>
        <p><strong>Registro ANS:</strong> {{ op.reg_ans }}</p>
        <p><strong>Local:</strong> {{ op.cidade }} - {{ op.uf }}</p>
        <p><strong>Modalidade:</strong> {{ op.modalidade }}</p>
      </div>
    </div>

    <h3>Histórico de Despesas</h3>
    <div class="list-container">
      <ul v-if="despesas.length">
        <li v-for="(d, index) in despesas" :key="index">
          <span class="date">{{ d.data_referencia }}</span>
          <span class="value"
            >R$ {{ d.valor_total.toLocaleString("pt-BR") }}</span
          >
        </li>
      </ul>
      <p v-else class="empty-msg">Sem despesas registradas.</p>
    </div>

    <router-link to="/operadoras" class="back-link"
      >← Voltar para Lista</router-link
    >
  </div>
</template>

<style scoped>
.container {
  padding: 20px 40px;
  max-width: 800px;
  margin: 0 auto;
}

.header-card {
  background: #4b3c5d;
  padding: 30px;
  border-radius: 10px;
  margin-bottom: 30px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

h1 {
  margin-top: 0;
  color: #e7bfa5;
  font-size: 1.8rem;
}
h3 {
  color: #c5a898;
  margin-top: 30px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-top: 20px;
}
.info-grid p {
  margin: 5px 0;
  color: #fff1ce;
}
strong {
  color: #c5a898;
}

.list-container {
  background: #4b3c5d;
  border-radius: 10px;
  padding: 10px;
}

ul {
  list-style: none;
  padding: 0;
  margin: 0;
}
li {
  display: flex;
  justify-content: space-between;
  padding: 15px;
  border-bottom: 1px solid rgba(197, 168, 152, 0.1);
}
li:last-child {
  border-bottom: none;
}

.date {
  color: #fff1ce;
}
.value {
  color: #e7bfa5;
  font-weight: bold;
}
.empty-msg {
  padding: 20px;
  text-align: center;
  color: rgba(255, 241, 206, 0.5);
  margin: 0;
}

.back-link {
  display: inline-block;
  margin-top: 30px;
  color: #c5a898;
  font-weight: bold;
}
.back-link:hover {
  color: #e7bfa5;
}
</style>
