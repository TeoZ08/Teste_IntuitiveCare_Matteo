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

<style>
body {
  margin: 0;
  font-family:
    -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu,
    Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
  background-color: #f5f7fa; /* Um cinza bem clarinho de fundo fica mais elegante */
  color: #2c3e50;
}
</style>
