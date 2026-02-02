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
    <h1>{{ op.razao_social }}</h1>
    <p>
      <strong>CNPJ:</strong> {{ op.cnpj }} | <strong>Registro ANS:</strong>
      {{ op.reg_ans }}
    </p>
    <p><strong>Local:</strong> {{ op.cidade }} - {{ op.uf }}</p>

    <h3>Histórico de Despesas</h3>
    <ul v-if="despesas.length">
      <li v-for="(d, index) in despesas" :key="index">
        {{ d.data_referencia }}:
        <strong>R$ {{ d.valor_total.toLocaleString("pt-BR") }}</strong>
      </li>
    </ul>
    <p v-else>Sem despesas registradas.</p>

    <router-link to="/operadoras">Voltar</router-link>
  </div>
</template>

<style scoped>
.container {
  padding: 20px;
}
</style>
