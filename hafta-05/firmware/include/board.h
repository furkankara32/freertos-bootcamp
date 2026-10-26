#pragma once
#include "stm32f4xx_hal.h"
extern UART_HandleTypeDef huart2, huart3;
void board_init(void);
uint32_t timer_us(void);
void fatal(const char *file, int line);
void app_init(void);
void app_button_isr(uint32_t now);
