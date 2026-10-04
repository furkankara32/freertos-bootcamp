#include "tim.h"
TIM_HandleTypeDef htim5;
void MX_TIM5_Init(void)
{
    __HAL_RCC_TIM5_CLK_ENABLE();
    htim5.Instance = TIM5;
    htim5.Init.Prescaler = 83;
    htim5.Init.CounterMode = TIM_COUNTERMODE_UP;
    htim5.Init.Period = 0xffffffffU;
    htim5.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
    htim5.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
    if (HAL_TIM_Base_Init(&htim5) != HAL_OK) Error_Handler();
}
