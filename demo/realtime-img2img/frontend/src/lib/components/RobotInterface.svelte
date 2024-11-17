<script lang="ts">
  import { addLog } from '$lib/store';
  import { ArrowUp, ArrowDown, ArrowLeft, ArrowRight } from 'lucide-svelte';
  import { writable } from 'svelte/store';

  const UART_SERVICE_UUID = '6e400001-b5a3-f393-e0a9-e50e24dcca9e';
  const UART_TX_CHARACTERISTIC_UUID = '6e400002-b5a3-f393-e0a9-e50e24dcca9e';
  const UART_RX_CHARACTERISTIC_UUID = '6e400003-b5a3-f393-e0a9-e50e24dcca9e';

  let device: BluetoothDevice | null = null;
  let server: BluetoothRemoteGATTServer | null = null;
  let rxCharacteristic: BluetoothRemoteGATTCharacteristic | null = null;
  let txCharacteristic;
  let activeButton: HTMLElement | null = null;

  const isConnected = writable(false);

  async function connectBluetooth() {
    try {
      device = await navigator.bluetooth.requestDevice({
        filters: [{ services: [UART_SERVICE_UUID] }, { namePrefix: 'BBC micro:bit' }]
      });

      addLog('Bluetooth接続を試みています...');
      server = await device.gatt.connect();
      const service = await server.getPrimaryService(UART_SERVICE_UUID);
      rxCharacteristic = await service.getCharacteristic(UART_RX_CHARACTERISTIC_UUID);
      txCharacteristic = await service.getCharacteristic(UART_TX_CHARACTERISTIC_UUID);

      await txCharacteristic.startNotifications();
      txCharacteristic.addEventListener('characteristicvaluechanged', handleNotifications);

      isConnected.set(true);
      addLog('Bluetooth接続に成功しました');
    } catch (error) {
      addLog(`接続エラー: ${error}`);
    }
  }

  async function disconnectBluetooth() {
    if (isConnected) {
      server = await device.gatt.disconnect();
      isConnected.set(false);
      addLog('Bluetooth接続を切断しました');
    }
  }

  async function toggleBluetooth() {
    if ($isConnected) {
      await disconnectBluetooth();
    } else {
      await connectBluetooth();
    }
  }

  function handleNotifications(event) {
    const value = new TextDecoder().decode(event.target.value);
    addLog(`[Microbit] 受信: ${value}`);
  }

  async function sendCommand(command) {
    if (!$isConnected) {
      addLog('[Microbit] Bluetooth未接続');
      return;
    }

    try {
      await rxCharacteristic.writeValue(new TextEncoder().encode(command + '\n'));
      addLog(`[Microbit] 送信: ${command}`);
    } catch (error) {
      addLog(`[Microbit] 送信エラー: ${error}`);
    }
  }

  function handleButtonPress(direction) {
    if (!isConnected) {
      addLog('先にBluetooth接続を行ってください');
      return;
    }
    sendCommand(direction);
  }

  function handleButtonRelease() {
    sendCommand('b'); // ブレーキコマンド
  }
</script>

<div class="grid grid-cols-2 gap-2">
  <div class="col-span-1 flex justify-end">
    <button
      on:click={toggleBluetooth}
      class={`aspect-square w-20 rounded-lg p-4 text-xs ${
        $isConnected ? 'bg-red-500 hover:bg-red-600' : 'bg-green-500 hover:bg-green-600'
      } text-white`}
    >
      {$isConnected ? 'Bluetooth切断' : 'Bluetooth接続'}
    </button>
  </div>
  <div class="col-span-1 mx-auto grid max-w-[240px] grid-cols-3 gap-2">
    <div></div>
    <!-- 中央の空セル -->
    <button
      class="flex aspect-square w-full items-center justify-center rounded-lg bg-gray-200 transition-colors hover:bg-gray-300"
      on:mousedown={() => handleButtonPress('w')}
      on:mouseup={handleButtonRelease}
    >
      <ArrowUp class="h-6 w-6" />
    </button>
    <div></div>
    <button
      class="flex aspect-square w-full items-center justify-center rounded-lg bg-gray-200 transition-colors hover:bg-gray-300"
      on:mousedown={() => handleButtonPress('a')}
      on:mouseup={handleButtonRelease}
    >
      <ArrowLeft class="h-6 w-6" />
    </button>
    <div></div>
    <button
      class="flex aspect-square w-full items-center justify-center rounded-lg bg-gray-200 transition-colors hover:bg-gray-300"
      on:mousedown={() => handleButtonPress('d')}
      on:mouseup={handleButtonRelease}
    >
      <ArrowRight class="h-6 w-6" />
    </button>
    <div></div>
    <button
      class="flex aspect-square w-full items-center justify-center rounded-lg bg-gray-200 transition-colors hover:bg-gray-300"
      on:mousedown={() => handleButtonPress('s')}
      on:mouseup={handleButtonRelease}
    >
      <ArrowDown class="h-6 w-6" />
    </button>
  </div>
</div>
