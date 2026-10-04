#ifndef APP_TRACE_H
#define APP_TRACE_H
#include <stdint.h>
#ifndef APP_TRACE
#define APP_TRACE 0
#endif
enum AppTraceEvent {
    TR_RUN_CONFIG, TR_RUN_ARMED, TR_RUN_STOP, TR_BTN_ACCEPT, TR_BTN_TASK,
    TR_BTN_READY, TR_BTN_ENQUEUE, TR_BTN_DROP, TR_BTN_TX_START, TR_BTN_TX_TC,
    TR_TEL_ENQUEUE, TR_TEL_DROP, TR_TEL_TX_START, TR_TEL_TX_TC,
    TR_WORK_BEGIN, TR_WORK_END, TR_TX_ERROR, TR_EVENT_COUNT
};
#if APP_TRACE
void AppTrace_Init(void);
void AppTrace_Event(unsigned event, uint32_t run, uint32_t id, uint32_t stamp, uint32_t detail);
void AppTrace_IsrEnter(void);
void AppTrace_IsrExit(void);
void AppTrace_Start(uint32_t duration_ms);
void AppTrace_Stop(void);
void AppTrace_Tick(void);
void AppTrace_NameQueue(void *queue, const char *name);
#else
#define AppTrace_Init() ((void)0)
#define AppTrace_Event(...) ((void)0)
#define AppTrace_IsrEnter() ((void)0)
#define AppTrace_IsrExit() ((void)0)
#define AppTrace_Start(...) ((void)0)
#define AppTrace_Stop() ((void)0)
#define AppTrace_Tick() ((void)0)
#define AppTrace_NameQueue(...) ((void)0)
#endif
#endif
