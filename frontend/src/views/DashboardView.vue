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

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: "bottom",
      labels: { color: "#fff1ce", padding: 20, font: { size: 14 } }, // Texto Creme
    },
  },
  scales: {
    y: {
      ticks: { color: "#c5a898" }, // Texto Rosé nos eixos
      grid: { color: "rgba(255, 241, 206, 0.1)" },
    },
    x: {
      ticks: { color: "#c5a898" },
      grid: { display: false },
    },
  },
};

onMounted(async () => {
  try {
    const response = await api.get("/estatisticas");
    stats.value = response.data;

    chartData.value = {
      labels: response.data.por_uf.slice(0, 10).map((i) => i.uf),
      datasets: [
        {
          label: "Despesas por Estado",
          backgroundColor: "#e7bfa5", // Color 3 - Barras Pêssego
          data: response.data.por_uf.slice(0, 10).map((i) => i.total),
          borderRadius: 4,
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
        <p>
          R$
          {{
            stats.total_despesas_periodo.toLocaleString("pt-BR", {
              minimumFractionDigits: 2,
            })
          }}
        </p>
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
  padding: 20px 40px;
  max-width: 1200px;
  margin: 0 auto;
}

h1 {
  color: #fff1ce;
  font-weight: 300;
  margin-bottom: 30px;
}

.dashboard {
  display: grid;
  gap: 30px;
}

.card {
  background: #4b3c5d; /* Color 5 - Cartão */
  padding: 25px;
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.card h3 {
  margin: 0;
  color: #c5a898;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 1px;
}
.card p {
  font-size: 2.5rem;
  color: #e7bfa5;
  margin: 10px 0 0 0;
  font-weight: 600;
}

.chart-container {
  background: #4b3c5d; /* Color 5 */
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  height: 400px;
  position: relative;
}
</style>
