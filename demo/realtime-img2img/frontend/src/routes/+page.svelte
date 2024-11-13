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
  import { Pause, Play } from 'lucide-svelte';

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

  function getStreamData() {
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
        await lcmLiveActions.start(getStreamData);
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

<main class="mx-auto space-y-6 p-4">
  <h1 class="mb-6 text-center text-3xl font-bold">Micro:bit x StreamDiffusion</h1>

  <Warning bind:message={warningMessage}></Warning>
  <section class="grid gap-6 md:grid-cols-2">
    <div class="col-span-1 flex justify-end">
      <div class="w-5/12 rounded-md">
        <VideoInput width={512} height={512}></VideoInput>
      </div>
    </div>
    <div class="col-span-1 flex justify-start">
      <div class="w-5/12 rounded-md">
        <ImagePlayer></ImagePlayer>
      </div>
    </div>
    <div class="col-span-2 flex flex-col items-center">
      <Button on:click={toggleLcmLive} {disabled} classList={'h-8 w-8 max-w-sm'}>
        {#if isLCMRunning}
          <Pause class="ml-1 h-6 w-6"></Pause>
        {:else}
          <Play class="ml-1 h-6 w-6"></Play>
        {/if}
      </Button>
      {#if pipelineParams}
        <PipelineOptions {pipelineParams} class="w-full max-w-xl"></PipelineOptions>
      {/if}
    </div>
    <div class="col-span-2 flex justify-center">
      <div class="w-4/6 rounded-md">
        <RobotInterface />
        <div class="w-4/6 rounded-md"></div>
      </div>
    </div>
  </section>
</main>
