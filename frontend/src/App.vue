<script setup>
import { RouterView } from "vue-router";
</script>

<template>
  <header>
    <div class="wrapper">
      <nav>
        <RouterLink to="/">Dashboard</RouterLink> |
        <RouterLink to="/operadoras">Operadoras</RouterLink>
      </nav>
    </div>
  </header>

  <main>
    <RouterView />
  </main>
</template>

<style scoped>
header {
  background-color: #333;
  padding: 1rem;
  margin-bottom: 20px;
}
nav {
  text-align: center;
}
nav a {
  color: white;
  text-decoration: none;
  font-weight: bold;
  font-size: 1.2rem;
  margin: 0 10px;
}
nav a.router-link-exact-active {
  color: #42b983;
}
</style>
