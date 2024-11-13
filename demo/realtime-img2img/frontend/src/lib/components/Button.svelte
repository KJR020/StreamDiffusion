<script lang="ts">
  export let classList: string = 'p-2';
  export let disabled: boolean = false;
  export let title: string = '';
</script>

<button class="button {classList}" on:click {disabled} {title}>
  <slot />
</button>

<style lang="postcss" scoped>
  .button {
    @apply rounded bg-blue-500 text-white hover:bg-blue-600 disabled:cursor-not-allowed disabled:bg-blue-300;
  }
</style>
