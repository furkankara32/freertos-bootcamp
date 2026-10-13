/* STM32F407G-DISC1, HSE 8 MHz, UART via external 3.3 V USB-TTL. */
#include "board.h"
#include "FreeRTOS.h"
#include "task.h"
#include "app_trace.h"
UART_HandleTypeDef huart2;
volatile const char *fault_file;
volatile int fault_line;


void fatal(const char *file, int line) {
    __disable_irq();
    fault_file = file; fault_line = line;
    __HAL_RCC_GPIOD_CLK_ENABLE();
    GPIOD->MODER = (GPIOD->MODER & ~(3UL << 28)) | (1UL << 28);
    GPIOD->BSRR = GPIO_PIN_14;
    for (;;) __NOP(); /* Inspect fault_file/fault_line in debugger. */
}
void vApplicationMallocFailedHook(void) { fatal(__FILE__, __LINE__); }
void vApplicationStackOverflowHook(TaskHandle_t task, char *name) {
    (void)task; (void)name; fatal(__FILE__, __LINE__);
}
void HardFault_Handler(void) { fatal(__FILE__, __LINE__); }
void MemManage_Handler(void) { fatal(__FILE__, __LINE__); }
void BusFault_Handler(void) { fatal(__FILE__, __LINE__); }
void UsageFault_Handler(void) { fatal(__FILE__, __LINE__); }
void SysTick_Handler(void) {
    HAL_IncTick();
    if (xTaskGetSchedulerState() != taskSCHEDULER_NOT_STARTED) {
        extern void xPortSysTickHandler(void);
        xPortSysTickHandler();
        AppTrace_Tick();
    }
}
void USART2_IRQHandler(void) {
    traceISR_ENTER(); HAL_UART_IRQHandler(&huart2);
    if(SCB->ICSR & SCB_ICSR_PENDSVSET_Msk) traceISR_EXIT_TO_SCHEDULER();
    else traceISR_EXIT();
}
uint32_t timer_us(void) { return TIM2->CNT; }

void board_init(void) {
    HAL_Init();
    HAL_NVIC_SetPriorityGrouping(NVIC_PRIORITYGROUP_4);
    __HAL_RCC_PWR_CLK_ENABLE();
    __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE1);
    RCC_OscInitTypeDef osc = {0};
    osc.OscillatorType = RCC_OSCILLATORTYPE_HSE;
    osc.HSEState = RCC_HSE_ON;
    osc.PLL.PLLState = RCC_PLL_ON;
    osc.PLL.PLLSource = RCC_PLLSOURCE_HSE;
    osc.PLL.PLLM = 8; osc.PLL.PLLN = 336;
    osc.PLL.PLLP = RCC_PLLP_DIV2; osc.PLL.PLLQ = 7;
    if (HAL_RCC_OscConfig(&osc) != HAL_OK) fatal(__FILE__, __LINE__);
    RCC_ClkInitTypeDef clk = {0};
    clk.ClockType = RCC_CLOCKTYPE_SYSCLK | RCC_CLOCKTYPE_HCLK | RCC_CLOCKTYPE_PCLK1 | RCC_CLOCKTYPE_PCLK2;
    clk.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
    clk.AHBCLKDivider = RCC_SYSCLK_DIV1;
    clk.APB1CLKDivider = RCC_HCLK_DIV4; clk.APB2CLKDivider = RCC_HCLK_DIV2;
    if (HAL_RCC_ClockConfig(&clk, FLASH_LATENCY_5) != HAL_OK) fatal(__FILE__, __LINE__);
    SystemCoreClockUpdate();
    if (SystemCoreClock != 168000000U) fatal(__FILE__, __LINE__);
    __HAL_RCC_GPIOA_CLK_ENABLE(); __HAL_RCC_GPIOD_CLK_ENABLE(); __HAL_RCC_SYSCFG_CLK_ENABLE();
    GPIO_InitTypeDef gpio = {0};
    gpio.Pin = GPIO_PIN_12 | GPIO_PIN_14; gpio.Mode = GPIO_MODE_OUTPUT_PP; gpio.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(GPIOD, &gpio);
    gpio.Pin = GPIO_PIN_2 | GPIO_PIN_3; gpio.Mode = GPIO_MODE_AF_PP;
    gpio.Pull = GPIO_PULLUP; gpio.Speed = GPIO_SPEED_FREQ_VERY_HIGH; gpio.Alternate = GPIO_AF7_USART2;
    HAL_GPIO_Init(GPIOA, &gpio);
    __HAL_RCC_USART2_CLK_ENABLE();
    huart2.Instance = USART2;
    huart2.Init.BaudRate = 230400;
    huart2.Init.WordLength = UART_WORDLENGTH_8B;
    huart2.Init.StopBits = UART_STOPBITS_1; huart2.Init.Parity = UART_PARITY_NONE;
    huart2.Init.Mode = UART_MODE_TX_RX; huart2.Init.HwFlowCtl = UART_HWCONTROL_NONE;
    huart2.Init.OverSampling = UART_OVERSAMPLING_16;
    if (HAL_UART_Init(&huart2) != HAL_OK) fatal(__FILE__, __LINE__);
    HAL_NVIC_SetPriority(USART2_IRQn, 6, 0); HAL_NVIC_EnableIRQ(USART2_IRQn);
    __HAL_RCC_TIM2_CLK_ENABLE();
    /* APB1 divider is 4: timer clock = 2 * 42 MHz = 84 MHz. */
    TIM2->PSC = (HAL_RCC_GetPCLK1Freq() * 2U / 1000000U) - 1U;
    TIM2->ARR = 0xFFFFFFFFU; TIM2->EGR = TIM_EGR_UG; TIM2->CR1 = TIM_CR1_CEN;
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    DWT->CYCCNT = 0; DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
}

