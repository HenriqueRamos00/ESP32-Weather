<script setup lang="ts"></script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-slate-900">
    <div class="bg-slate-800 p-8 rounded-xl shadow-lg w-full max-w-sm">
      <h1 class="text-2xl font-bold mb-6 text-white text-center">Login</h1>

      <form class="space-y-4">
        <div>
          <label class="block text-sm text-slate-300 mb-1">Email</label>
          <input
            type="email"
            class="w-full px-3 py-2 rounded-md bg-slate-900 text-white border border-slate-700 focus:outline-none focus:ring-2 focus:ring-sky-500"
          />
        </div>
        <div>
          <label class="block text-sm text-slate-300 mb-1">Password</label>
          <input
            type="password"
            class="w-full px-3 py-2 rounded-md bg-slate-900 text-white border border-slate-700 focus:outline-none focus:ring-2 focus:ring-sky-500"
          />
        </div>
        <button
          type="submit"
          class="w-full py-2 rounded-md bg-sky-600 hover:bg-sky-700 text-white font-medium"
        >
          Sign in
        </button>
      </form>
    </div>
  </div>
</template>
