import { derived, get, writable, type Readable, type Writable } from 'svelte/store';

export const pipelineValues: Writable<Record<string, any>> = writable({});
export const deboucedPipelineValues: Readable<Record<string, any>> = derived(
  pipelineValues,
  ($pipelineValues, set) => {
    const debounced = setTimeout(() => {
      set($pipelineValues);
    }, 100);
    return () => clearTimeout(debounced);
  }
);

export const logs = writable<string[]>([]);

export function addLog(message: string | null) {
  logs.update((currentLogs) => [
    ...currentLogs,
    `${new Date().toLocaleString('ja-JP', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })} ${message}`
  ]);
}

export const getPipelineValues = () => get(pipelineValues);
