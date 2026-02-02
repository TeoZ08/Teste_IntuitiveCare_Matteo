<script setup>
import { ref, onMounted } from "vue";
import api from "../services/api";
import { Bar } from "vue-chartjs";
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
} from "chart.js";

ChartJS.register(
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
);

const stats = ref(null);
const chartData = ref(null);
const chartOptions = { responsive: true };

onMounted(async () => {
  try {
    const response = await api.get("/estatisticas");
    stats.value = response.data;

    // Configura o gráfico com os dados da API
    chartData.value = {
      labels: response.data.por_uf.slice(0, 10).map((i) => i.uf), // Top 10 UFs
      datasets: [
        {
          label: "Despesas por Estado",
          backgroundColor: "#42b983",
          data: response.data.por_uf.slice(0, 10).map((i) => i.total),
        },
      ],
    };
  } catch (error) {
    console.error(error);
  }
});
</script>

<template>
  <div class="container">
    <h1>Dashboard Financeiro</h1>
    <div v-if="stats" class="dashboard">
      <div class="card">
        <h3>Total Geral</h3>
        <p>R$ {{ stats.total_despesas_periodo.toLocaleString("pt-BR") }}</p>
      </div>

      <div class="chart-container" v-if="chartData">
        <Bar :data="chartData" :options="chartOptions" />
      </div>
    </div>
    <div v-else>Carregando dados...</div>
  </div>
</template>

<style scoped>
.container {
  padding: 20px;
}
.card {
  background: #f4f4f4;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
}
.card h3 {
  margin: 0;
  color: #555;
}
.card p {
  font-size: 1.5em;
  font-weight: bold;
  color: #2c3e50;
}
</style>
