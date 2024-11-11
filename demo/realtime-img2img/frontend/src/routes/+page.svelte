<script lang="ts">
  import { onMount } from 'svelte';
  import type { Fields, PipelineInfo } from '$lib/types';
  import { PipelineMode } from '$lib/types';
  import ImagePlayer from '$lib/components/ImagePlayer.svelte';
  import VideoInput from '$lib/components/VideoInput.svelte';
  import Button from '$lib/components/Button.svelte';
  import PipelineOptions from '$lib/components/PipelineOptions.svelte';
  import Spinner from '$lib/icons/spinner.svelte';
  import Warning from '$lib/components/Warning.svelte';
  import { lcmLiveStatus, lcmLiveActions, LCMLiveStatus } from '$lib/lcmLive';
  import { mediaStreamActions, onFrameChangeStore } from '$lib/mediaStream';
  import { getPipelineValues, deboucedPipelineValues } from '$lib/store';
  import RobotInterface from '$lib/components/RobotInterface.svelte';

  let pipelineParams: Fields;
  let pipelineInfo: PipelineInfo;
  let pageContent: string;
  let isImageMode: boolean = false;
  let maxQueueSize: number = 0;
  let currentQueueSize: number = 0;
  let queueCheckerRunning: boolean = false;
  let warningMessage: string = '';

  onMount(() => {
    getSettings();
  });

  async function getSettings() {
    const settings = await fetch('/api/settings').then((r) => r.json());
    pipelineParams = settings.input_params.properties;
    pipelineInfo = settings.info.properties;
    isImageMode = pipelineInfo.input_mode.default === PipelineMode.IMAGE;
    maxQueueSize = settings.max_queue_size;
    pageContent = settings.page_content;
    console.log(pipelineParams);
    toggleQueueChecker(true);
  }

  function toggleQueueChecker(start: boolean) {
    queueCheckerRunning = start && maxQueueSize > 0;
    if (start) {
      getQueueSize();
    }
  }

  async function getQueueSize() {
    if (!queueCheckerRunning) {
      return;
    }
    const data = await fetch('/api/queue').then((r) => r.json());
    currentQueueSize = data.queue_size;
    setTimeout(getQueueSize, 10000);
  }

  function getSreamdata() {
    if (isImageMode) {
      return [getPipelineValues(), $onFrameChangeStore?.blob];
    } else {
      return [$deboucedPipelineValues];
    }
  }

  $: isLCMRunning = $lcmLiveStatus !== LCMLiveStatus.DISCONNECTED;
  $: if ($lcmLiveStatus === LCMLiveStatus.TIMEOUT) {
    warningMessage = 'Session timed out. Please try again.';
  }

  let disabled = false;

  async function toggleLcmLive() {
    try {
      if (!isLCMRunning) {
        if (isImageMode) {
          await mediaStreamActions.enumerateDevices();
          await mediaStreamActions.start();
        }
        disabled = true;
        await lcmLiveActions.start(getSreamdata);
        disabled = false;
        toggleQueueChecker(false);
      } else {
        if (isImageMode) {
          mediaStreamActions.stop();
        }
        lcmLiveActions.stop();
        toggleQueueChecker(true);
      }
    } catch (e) {
      warningMessage = e instanceof Error ? e.message : '';
      disabled = false;
      toggleQueueChecker(true);
    }
  }
</script>

<main class="mx-auto max-w-6xl space-y-6 p-4">
  <h1 class="mb-6 text-center text-3xl font-bold">Micro:bit Bluetooth コントローラー</h1>

  <Warning bind:message={warningMessage}></Warning>
  <section class="text-center">
    {#if maxQueueSize > 0}
      <p class="text-sm text-gray-700">
        Current queue size: <span class="font-semibold">{currentQueueSize}</span>. Max: {maxQueueSize}.
        <a
          href="https://huggingface.co/spaces/radames/Real-Time-Latent-Consistency-Model?duplicate=true"
          target="_blank"
          class="text-blue-500 underline hover:no-underline"
        >
          Duplicate
        </a>
        to run it on your own GPU.
      </p>
    {/if}
  </section>

  {#if pipelineParams}
    <section class="grid gap-6 md:grid-cols-2">
      {#if isImageMode}
        <div class="flex flex-col items-center">
          <VideoInput width="512" height="512" class="rounded-md border shadow-md"></VideoInput>
        </div>
      {/if}
      <div class={isImageMode ? 'col-start-2' : 'col-span-2'}>
        <ImagePlayer class="rounded-md shadow-md"></ImagePlayer>
      </div>

      <div class="col-span-2 flex flex-col items-center space-y-4">
        <Button
          on:click={toggleLcmLive}
          {disabled}
          class="w-full max-w-sm rounded-lg bg-blue-500 px-4 py-2 text-lg text-white shadow-md hover:bg-blue-600"
        >
          {#if isLCMRunning}
            Stop
          {:else}
            Start
          {/if}
        </Button>
        <div class="flex flex-wrap justify-center gap-4">
          <RobotInterface />
          <PipelineOptions {pipelineParams} class="w-full max-w-xl"></PipelineOptions>
        </div>
      </div>
    </section>
  {:else}
    <div class="flex flex-col items-center justify-center gap-4 py-32">
      <Spinner class="animate-spin text-gray-400"></Spinner>
      <p class="text-lg font-medium">Loading...</p>
    </div>
  {/if}
</main>
