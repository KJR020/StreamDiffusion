<script lang="ts">
  const UART_SERVICE_UUID = '6e400001-b5a3-f393-e0a9-e50e24dcca9e';
  const UART_TX_CHARACTERISTIC_UUID = '6e400002-b5a3-f393-e0a9-e50e24dcca9e';
  const UART_RX_CHARACTERISTIC_UUID = '6e400003-b5a3-f393-e0a9-e50e24dcca9e';

  let device: BluetoothDevice | null = null;
  let server: BluetoothRemoteGATTServer | null = null;
  let rxCharacteristic: BluetoothRemoteGATTCharacteristic | null = null;
  let txCharacteristic;
  let isConnected: boolean = false;
  let activeButton: HTMLElement | null = null;
  let logs: string[] = [];

  function addLog(message: string | null) {
    logs = [...logs, `${new Date().toLocaleTimeString()} ${message}`];
  }

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

      isConnected = true;
      addLog('Bluetooth接続に成功しました');
    } catch (error) {
      addLog(`接続エラー: ${error}`);
    }
  }

  async function disconnectBluetooth() {
    if (isConnected) {
      server = await device.gatt.disconnect();
      isConnected = false;
      addLog('Bluetooth接続を切断しました');
    }
  }

  function handleNotifications(event) {
    const value = new TextDecoder().decode(event.target.value);
    addLog(`受信: ${value}`);
  }

  async function sendCommand(command) {
    if (!isConnected) {
      addLog('接続されていません');
      return;
    }

    try {
      await rxCharacteristic.writeValue(new TextEncoder().encode(command + '\n'));
      addLog(`送信: ${command}`);
    } catch (error) {
      addLog(`送信エラー: ${error}`);
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

<div class="connection-status">
  <span class="status-indicator" class:isConnected></span>
  <span class="status-text">{isConnected ? '接続中' : '未接続'}</span>
</div>

<div class="bluetooth-controls">
  <button class="bluetooth-button connect" on:click={connectBluetooth}>Bluetooth接続</button>
  <button class="bluetooth-button disconnect" on:click={disconnectBluetooth}>接続解除</button>
</div>

<div class="controller">
  <button
    class="button up"
    on:mousedown={() => handleButtonPress('w')}
    on:mouseup={handleButtonRelease}>↑</button
  >
  <button
    class="button down"
    on:mousedown={() => handleButtonPress('s')}
    on:mouseup={handleButtonRelease}>↓</button
  >
  <button
    class="button left"
    on:mousedown={() => handleButtonPress('a')}
    on:mouseup={handleButtonRelease}>←</button
  >
  <button
    class="button right"
    on:mousedown={() => handleButtonPress('d')}
    on:mouseup={handleButtonRelease}>→</button
  >
</div>

<div id="log">
  {#each logs as log}
    <p>{log}</p>
  {/each}
</div>

<style>
  body {
    font-family: Arial, sans-serif;
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
    text-align: center;
  }

  h1 {
    color: #333;
    margin-bottom: 30px;
  }

  .controller {
    display: inline-block;
    position: relative;
    width: 240px;
    height: 240px;
  }

  .button {
    position: absolute;
    width: 60px;
    height: 60px;
    background: #f0f0f0;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    transition: background-color 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
  }

  .button:hover {
    background: #e0e0e0;
  }

  .button.active {
    background: #4a90e2;
    color: white;
  }

  .up {
    top: 0;
    left: 90px;
  }
  .down {
    bottom: 0;
    left: 90px;
  }
  .left {
    top: 90px;
    left: 0;
  }
  .right {
    top: 90px;
    right: 0;
  }

  .bluetooth-controls {
    margin: 20px 0;
  }

  .bluetooth-button {
    padding: 10px 20px;
    margin: 0 10px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    transition: background-color 0.2s;
  }

  .connect {
    background: #4caf50;
    color: white;
  }

  .disconnect {
    background: #f44336;
    color: white;
  }

  .bluetooth-button:hover {
    opacity: 0.9;
  }

  .connection-status {
    margin: 10px 0;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
  }

  .status-indicator {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background-color: #ff4444;
    transition: background-color 0.3s;
  }

  .status-indicator.connected {
    background-color: #4caf50;
  }

  #log {
    margin-top: 20px;
    padding: 10px;
    background: #f5f5f5;
    border-radius: 5px;
    height: 200px;
    overflow-y: auto;
    text-align: left;
    border: 1px solid #ddd;
    font-family: monospace;
  }

  #log p {
    margin: 5px 0;
    padding: 2px 0;
    border-bottom: 1px solid #eee;
  }
</style>
