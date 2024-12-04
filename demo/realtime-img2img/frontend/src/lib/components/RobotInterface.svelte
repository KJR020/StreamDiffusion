<script lang="ts">
  import { addLog } from '$lib/store';
  import { ArrowUp, ArrowDown, ArrowLeft, ArrowRight } from 'lucide-svelte';
  import { onMount } from 'svelte';
  import { writable } from 'svelte/store';

  const UART_SERVICE_UUID = '6e400001-b5a3-f393-e0a9-e50e24dcca9e';
  const UART_TX_CHARACTERISTIC_UUID = '6e400002-b5a3-f393-e0a9-e50e24dcca9e';
  const UART_RX_CHARACTERISTIC_UUID = '6e400003-b5a3-f393-e0a9-e50e24dcca9e';

  let device: BluetoothDevice | null = null;
  let server: BluetoothRemoteGATTServer | null = null;
  let rxCharacteristic: BluetoothRemoteGATTCharacteristic | null = null;
  let txCharacteristic: BluetoothRemoteGATTCharacteristic | null = null;

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
    if ($isConnected) {
      server?.disconnect();
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
      await rxCharacteristic?.writeValue(new TextEncoder().encode(command + '\n'));
      addLog(`[Microbit] 送信: ${command}`);
    } catch (error) {
      addLog(`[Microbit] 送信エラー: ${error}`);
    }
  }

  function handleButtonPress(direction) {
    if (!$isConnected) {
      addLog('先にBluetooth接続を行ってください');
      return;
    }
    sendCommand(direction);
  }

  function handleButtonRelease() {
    sendCommand('b'); // ブレーキコマンド
  }

  // ゲームパッドの状態管理
  let gamepadInterval;
  let previousButtons = [];
  let previousAxes = [];

  // アクティブなキーを追跡するためのセット
  const activeKeys = new Set();
  let currentCommand = null; // 現在送信中のコマンド

  // キーの状態を管理する関数
  function updateKeyState(key, isPressed) {
    const previousCommand = currentCommand;

    if (isPressed) {
      activeKeys.add(key);
    } else {
      activeKeys.delete(key);
    }

    // アクティブなキーがある場合は最後に押されたキーのコマンドを設定
    if (activeKeys.size > 0) {
      currentCommand = Array.from(activeKeys).pop();
    } else {
      currentCommand = 'b'; // ブレーキ
    }

    // コマンドが変化した時のみ送信
    if (currentCommand !== previousCommand) {
      sendCommand(currentCommand);
    }
  }

  // ゲームパッドの状態を定期的にチェック
  function startGamepadPolling() {
    if (gamepadInterval) return;

    let previousState = {
      buttons: new Array(16).fill(false),
      axes: new Array(4).fill(0)
    };

    gamepadInterval = setInterval(() => {
      const gamepad = navigator.getGamepads()[0];
      if (!gamepad) return;

      // 十字キーの状態チェック
      const buttonMappings = [
        { index: 12, key: 'w' }, // 上
        { index: 13, key: 's' }, // 下
        { index: 14, key: 'a' }, // 左
        { index: 15, key: 'd' } // 右
      ];

      // ボタンの状態変化を確認
      buttonMappings.forEach(({ index, key }) => {
        const isPressed = gamepad.buttons[index].pressed;
        if (isPressed !== previousState.buttons[index]) {
          updateKeyState(key, isPressed);
          previousState.buttons[index] = isPressed;
        }
      });

      // アナログスティックの処理
      const STICK_THRESHOLD = 0.5;
      const axes = gamepad.axes;

      // 垂直方向（axes[1]）の状態変化を確認
      const upPressed = axes[1] < -STICK_THRESHOLD;
      const downPressed = axes[1] > STICK_THRESHOLD;
      if (upPressed !== previousState.axes[1] < -STICK_THRESHOLD) {
        updateKeyState('w', upPressed);
      }
      if (downPressed !== previousState.axes[1] > STICK_THRESHOLD) {
        updateKeyState('s', downPressed);
      }

      // 水平方向（axes[0]）の状態変化を確認
      const leftPressed = axes[0] < -STICK_THRESHOLD;
      const rightPressed = axes[0] > STICK_THRESHOLD;
      if (leftPressed !== previousState.axes[0] < -STICK_THRESHOLD) {
        updateKeyState('a', leftPressed);
      }
      if (rightPressed !== previousState.axes[0] > STICK_THRESHOLD) {
        updateKeyState('d', rightPressed);
      }

      // 現在の状態を保存
      previousState.axes = [...axes];
    }, 100);
  }

  // ポーリングの停止
  function stopGamepadPolling() {
    if (gamepadInterval) {
      clearInterval(gamepadInterval);
      gamepadInterval = null;
    }
  }

  // ゲームパッドの接続状態を管理
  let gamepadConnected = false;

  function updateGamepadStatus(connected) {
    gamepadConnected = connected;
  }

  onMount(() => {
    // イベントリスナーでゲームパッドの接続/切断を検出
    window.addEventListener('gamepadconnected', (e) => {
      addLog(`ゲームパッド接続: ${e.gamepad.id}`);
      startGamepadPolling();
      updateGamepadStatus(true);
    });

    window.addEventListener('gamepaddisconnected', (e) => {
      addLog(`ゲームパッド切断: ${e.gamepad.id}`);
      stopGamepadPolling();
      updateGamepadStatus(false);
    });
  });
</script>

<div class="grid grid-cols-2 gap-2">
  <div class="col-span-1 flex flex-col items-end">
    <button
      on:click={toggleBluetooth}
      class={`aspect-square w-20 rounded-lg p-4 text-xs ${
        $isConnected ? 'bg-red-500 hover:bg-red-600' : 'bg-green-500 hover:bg-green-600'
      } text-white`}
    >
      {$isConnected ? 'Bluetooth切断' : 'Bluetooth接続'}
    </button>
    {#if gamepadConnected}
      <div class="mt-2 text-green-600">🎮 ゲームパッド接続中</div>
    {/if}
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
