#ifndef APP_H
#define APP_H
#include <stdint.h>
void App_Init(void);
void App_ButtonIRQ(uint32_t now);
uint32_t App_Now(void);
void App_TelemetryTask(void);
void App_ButtonTask(void);
void App_UartTask(void);
#endif
