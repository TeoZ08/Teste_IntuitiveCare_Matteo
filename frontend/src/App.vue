<script setup>
import { RouterView } from "vue-router";
</script>

<template>
  <header>
    <div class="wrapper">
      <nav>
        <RouterLink to="/">Dashboard</RouterLink>
        <RouterLink to="/operadoras">Operadoras</RouterLink>
      </nav>
    </div>
  </header>

  <main>
    <RouterView />
  </main>
</template>

<style>
/* --- ESTILO GLOBAL (Reset + Cores) --- */
body {
  margin: 0;
  background-color: #21203f; /* Color 1 - Fundo */
  color: #fff1ce; /* Color 2 - Texto */
  font-family: "Poppins", sans-serif;
  -webkit-font-smoothing: antialiased;
}

a {
  color: #e7bfa5; /* Color 3 - Links */
  text-decoration: none;
  transition: opacity 0.3s;
}

a:hover {
  opacity: 0.8;
}
</style>

<style scoped>
header {
  background-color: #4b3c5d; /* Color 5 - Navbar */
  padding: 1.5rem;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
  margin-bottom: 30px;
}

nav {
  display: flex;
  justify-content: center;
  gap: 30px;
}

nav a {
  color: #fff1ce; /* Color 2 */
  font-weight: 600;
  font-size: 1.1rem;
  text-transform: uppercase;
  letter-spacing: 1px;
}

nav a.router-link-exact-active {
  color: #e7bfa5; /* Color 3 - Ativo */
  border-bottom: 2px solid #e7bfa5;
}
</style>
