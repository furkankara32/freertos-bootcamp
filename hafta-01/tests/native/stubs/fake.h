#ifndef FAKE_H
#define FAKE_H
#include <stdint.h>
#include <stddef.h>
typedef unsigned TickType_t;
typedef unsigned UBaseType_t;
typedef int BaseType_t;
typedef void *TaskHandle_t;
typedef struct FakeQueue *QueueHandle_t;
typedef struct {unsigned CR, CNT, BRR;} Peripheral;
extern Peripheral timer,uart,dma;
#define TIM5 (&timer)
#define USART2 (&uart)
#define DMA1_Stream6 (&dma)
typedef struct {int ErrorCode;} DMA_HandleTypeDef;
typedef struct {DMA_HandleTypeDef *hdmatx;int RxState;} UART_HandleTypeDef;
typedef int TIM_HandleTypeDef;
typedef int HAL_StatusTypeDef;
extern UART_HandleTypeDef huart2;
extern TIM_HandleTypeDef htim5;
extern unsigned SystemCoreClock;
#define HAL_OK 0
#define HAL_DMA_ERROR_NONE 0
#define HAL_UART_STATE_READY 0
#define UART_FLAG_TC 0
#define DMA1_Stream6_IRQn 0
#define EXTI0_IRQn 0
#define DMA_SxCR_EN 1
#define GPIO_PIN_0 1
#define pdTRUE 1
#define pdFALSE 0
#define pdPASS 1
#define portMAX_DELAY 0xffffffffU
#define eSetBits 0
#define configTICK_RATE_HZ 1000
#define tskKERNEL_VERSION_NUMBER "V10.3.1"
#define pdMS_TO_TICKS(x) (x)
#define taskENTER_CRITICAL() ((void)0)
#define taskEXIT_CRITICAL() ((void)0)
#define taskENTER_CRITICAL_FROM_ISR() 0
#define taskEXIT_CRITICAL_FROM_ISR(x) ((void)(x))
#define taskDISABLE_INTERRUPTS() ((void)0)
#define portYIELD_FROM_ISR(x) ((void)(x))
#define __HAL_UART_CLEAR_FLAG(a,b) ((void)0)
#define __HAL_GPIO_EXTI_CLEAR_IT(a) ((void)0)
void Error_Handler(void);
int HAL_TIM_Base_Start(TIM_HandleTypeDef *);
int HAL_UART_Receive_IT(UART_HandleTypeDef *,uint8_t *,unsigned);
int HAL_UART_Transmit_DMA(UART_HandleTypeDef *,uint8_t *,unsigned);
int HAL_UART_AbortTransmit(UART_HandleTypeDef *);
void HAL_NVIC_ClearPendingIRQ(int);
void HAL_NVIC_SetPriority(int,int,int);
void HAL_NVIC_EnableIRQ(int);
unsigned HAL_RCC_GetPCLK1Freq(void);
QueueHandle_t xQueueCreate(unsigned,unsigned);
int xQueueSend(QueueHandle_t,const void *,unsigned);
int xQueueSendFromISR(QueueHandle_t,const void *,int *);
int xQueueReceive(QueueHandle_t,void *,unsigned);
unsigned uxQueueMessagesWaiting(QueueHandle_t);
unsigned uxQueueMessagesWaitingFromISR(QueueHandle_t);
unsigned xTaskGetTickCount(void);
TaskHandle_t xTaskGetCurrentTaskHandle(void);
int xTaskNotify(TaskHandle_t,unsigned,int);
int xTaskNotifyFromISR(TaskHandle_t,unsigned,int,int *);
int xTaskNotifyWait(unsigned,unsigned,unsigned *,unsigned);
unsigned ulTaskNotifyValueClear(TaskHandle_t,unsigned);
void vTaskDelay(unsigned);
void vTaskDelayUntil(unsigned *,unsigned);
unsigned xPortGetMinimumEverFreeHeapSize(void);
unsigned uxTaskGetStackHighWaterMark(TaskHandle_t);
#endif
