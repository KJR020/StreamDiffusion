<script lang="ts">
  import { logs } from '$lib/store';
  import { LogsIcon } from 'lucide-svelte';
  import { onDestroy } from 'svelte';
  let logList: string[] = [];
  const unsubscribe = logs.subscribe((value) => {
    logList = value;
  });
  onDestroy(unsubscribe);
</script>

<div class="col-span-3 w-10/12 rounded-lg border border-gray-200 bg-gray-50 p-4">
  <div class="mb-2 flex items-center justify-between">
    <h2 class="flex items-center text-sm font-medium text-gray-700"><LogsIcon /> LogConsole</h2>
  </div>
  <div class="log-container h-32 overflow-auto bg-gray-100 p-4">
    {#each logList as log}
      <div class="py-1 text-sm">{log}</div>
    {/each}
  </div>
</div>
