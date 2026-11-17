# SDKconfig Common Knobs

Access via `idf.py menuconfig`.

## WiFi

| Symbol | Default | Notes |
|--------|---------|-------|
| `CONFIG_ESP_WIFI_STATIC_RX_BUFFER_NUM` | 10 | Increase to 16-32 for high-throughput UDP |
| `CONFIG_ESP_WIFI_DYNAMIC_RX_BUFFER_NUM` | 32 | Keep default |
| `CONFIG_ESP_WIFI_TX_BUFFER_TYPE` | Dynamic | Dynamic saves RAM |
| `CONFIG_ESP_WIFI_STATIC_TX_BUFFER_NUM` | 16 | Only used if static TX selected |
| `CONFIG_ESP_WIFI_CSI_ENABLED` | n | Disable if not using channel state info |
| `CONFIG_ESP_WIFI_AMPDU_TX_ENABLED` | y | Enable for throughput |
| `CONFIG_ESP_WIFI_AMPDU_RX_ENABLED` | y | Enable for throughput |

## Logging

| Symbol | Default | Notes |
|--------|---------|-------|
| `CONFIG_LOG_DEFAULT_LEVEL` | WARN | Change to INFO/VERBOSE for debug |
| `CONFIG_LOG_TIMESTAMP_SOURCE_RTOS` | y | Use system time for log timestamps |
| `CONFIG_LOG_MAXIMUM_LEVEL` | WARN | Must be >= default level to compile in |

## SPI RAM

| Symbol | Default | Notes |
|--------|---------|-------|
| `CONFIG_SPIRAM` | n | Enable if board has external PSRAM |
| `CONFIG_SPIRAM_TYPE_AUTO` | y | Auto-detect PSRAM type |
| `CONFIG_SPIRAM_USE` | malloc | `malloc`/`cap`/`exec` strategies |
| `CONFIG_SPIRAM_MALLOC_ALWAYSINTERNAL` | 16384 | Bytes always allocated from internal RAM |
| `CONFIG_SPIRAM_CACHE_WORKAROUND` | y | Needed if PSRAM + cache enabled |

## Partition Table

| Symbol | Default | Notes |
|--------|---------|-------|
| `CONFIG_PARTITION_TABLE_SINGLE_APP` | y | Single app, no OTA |
| `CONFIG_PARTITION_TABLE_TWO_OTA` | n | OTA with two app slots |
| `CONFIG_PARTITION_TABLE_CUSTOM` | n | Custom partitions.csv |
| `CONFIG_PARTITION_TABLE_FILENAME` | partitions.csv | Only used for custom |

## Task Stack

| Symbol | Default | Notes |
|--------|---------|-------|
| `CONFIG_MAIN_TASK_STACK_SIZE` | 3072 | Increase for complex main tasks |
| `CONFIG_ESP_NETIF_TCPIP_LWIP` | y | lwIP TCP/IP stack |

## SPI Slave (for K230 link)

| Symbol | Default | Notes |
|--------|---------|-------|
| `CONFIG_SPI_SLAVE_ISR_IN_IRAM` | n | Set y if SPI ISR must run while flash cache is suspended |
| `CONFIG_SPI_SLAVE_BUSY_WAIT_READY` | y | Wait for SPI Slave ready before flushing |
