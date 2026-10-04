"""One-time, checked integration into the copied V2 sources (never week 1)."""
from pathlib import Path
import shutil, re, json, subprocess
W=Path(__file__).resolve().parents[1]
P=W/'projects/v2/firmware/Homework_001'
K=P/'Middlewares/Third_Party/FreeRTOS/Source'
V=P/'Middlewares/SEGGER'
def put(p,s):
    p.parent.mkdir(parents=True,exist_ok=True); p.write_text(s,encoding='utf-8')
def edit(p,a,b,count=1):
    s=p.read_text(encoding='utf-8'); assert s.count(a)==count,(str(p),a,s.count(a));put(p,s.replace(a,b))
for dirname, src, patterns in [
    ('SYSVIEW',W/'tools/SystemView-source/SYSVIEW',['*.c','*.h']),
    ('SEGGER',W/'tools/SystemView-source/SEGGER',['*.h']),
    ('RTT',W/'tools/RTT-source/RTT',['SEGGER_RTT.c','*.h']),
    ('FreeRTOS',W/'tools/SystemView-source/Sample/FreeRTOSV10',['*.c','*.h'])]:
    for pat in patterns:
        for f in src.glob(pat):
            dest=V/dirname/f.name; dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,dest)
for name,src in [('LICENSE-SystemView.md',W/'tools/SystemView-source/LICENSE.md'),('LICENSE-RTT.md',W/'tools/RTT-source/LICENSE.md')]:
    if src.exists():shutil.copy2(src,V/name)
put(V/'Config/SEGGER_SYSVIEW_Conf.h','''#ifndef SEGGER_SYSVIEW_CONF_H
#define SEGGER_SYSVIEW_CONF_H
#define SEGGER_SYSVIEW_RTT_BUFFER_SIZE 32768
#define SEGGER_SYSVIEW_RTT_CHANNEL 1
#define SEGGER_SYSVIEW_TIMESTAMP_BITS 32
#define SEGGER_SYSVIEW_GET_TIMESTAMP() (*(volatile unsigned long *)0xE0001004UL)
#endif
''')
put(V/'Config/SEGGER_RTT_Conf.h','''#ifndef SEGGER_RTT_CONF_H
#define SEGGER_RTT_CONF_H
#define SEGGER_RTT_MAX_INTERRUPT_PRIORITY 0x50
#define SEGGER_RTT_MODE_DEFAULT SEGGER_RTT_MODE_NO_BLOCK_SKIP
#endif
''')
# Preserve IRQ wrappers as the single owner of peripheral exit events.
# portYIELD_FROM_ISR is intentionally untouched: HAL may invoke multiple callbacks.
f=P/'Inc/FreeRTOSConfig.h'
edit(f,'#endif /* FREERTOS_CONFIG_H */','''/* Week 2: retain kernel 10.3.1, add legacy SystemView hooks. */
#ifndef APP_TRACE
#define APP_TRACE 1
#endif
#if APP_TRACE
#define INCLUDE_xTaskGetIdleTaskHandle 1
#define USE_LEGACY_TRACE_API 1
#include "SEGGER_SYSVIEW_FreeRTOS.h"
#endif
#endif /* FREERTOS_CONFIG_H */''')
f=K/'include/FreeRTOS.h'
anchor='#ifndef traceQUEUE_CREATE'
pos=f.read_text().index(anchor)
s=f.read_text(); defaults=''
for macro,params in [('traceREADDED_TASK_TO_READY_STATE','pxTCB'),('traceMOVED_TASK_TO_DELAYED_LIST',''),('traceMOVED_TASK_TO_OVERFLOW_DELAYED_LIST',''),('traceMOVED_TASK_TO_SUSPENDED_LIST','pxTCB'),('traceISR_ENTER',''),('traceISR_EXIT',''),('traceISR_EXIT_TO_SCHEDULER','')]:
    defaults+=f'#ifndef {macro}\n#define {macro}({params})\n#endif\n'
put(f,s[:pos]+defaults+'\n'+s[pos:])
f=K/'tasks.c';s=f.read_text()
start=s.index('#define prvAddTaskToReadyList(');end=s.index('/*----',start)
macro=s[start:end].replace('prvAddTaskToReadyList','prvReaddTaskToReadyList').replace('traceMOVED_TASK_TO_READY_STATE','traceREADDED_TASK_TO_READY_STATE')
s=s[:end]+'/* SystemView: reprioritizing an already-ready task is not a wakeup. */\n'+macro+s[end:]
for fn in ['void vTaskPrioritySet(', 'BaseType_t xTaskPriorityInherit(', 'BaseType_t xTaskPriorityDisinherit(', 'void vTaskPriorityDisinheritAfterTimeout(']:
    start=s.index(fn);end=s.index('/*-----------------------------------------------------------*/',start)
    section=s[start:end];assert 'prvAddTaskToReadyList' in section,fn
    s=s[:start]+section.replace('prvAddTaskToReadyList','prvReaddTaskToReadyList')+s[end:]
patterns=[(r'(?m)^(\s*)vListInsertEnd\( &xSuspendedTaskList, &\( (pxTCB|pxCurrentTCB)->xStateListItem \) \);',lambda m:f'{m[1]}traceMOVED_TASK_TO_SUSPENDED_LIST({m[2]});\n{m[0]}'),
(r'(?m)^(\s*)vListInsert\( pxOverflowDelayedTaskList, &\( pxCurrentTCB->xStateListItem \) \);',lambda m:f'{m[1]}traceMOVED_TASK_TO_OVERFLOW_DELAYED_LIST();\n{m[0]}'),
(r'(?m)^(\s*)vListInsert\( pxDelayedTaskList, &\( pxCurrentTCB->xStateListItem \) \);',lambda m:f'{m[1]}traceMOVED_TASK_TO_DELAYED_LIST();\n{m[0]}')]
for pat,rep in patterns:
    s,n=re.subn(pat,rep,s);assert n==2,(pat,n)
put(f,s)
# Sample adapter uses a stale variable name in the newer disinherit-after-timeout hook.
f=V/'FreeRTOS/SEGGER_SYSVIEW_FreeRTOS.h'
s=f.read_text();s=re.sub(r'(#define traceTASK_PRIORITY_(?:DIS)?INHERIT[^\n]+)\(U32\)pxMutexHolder',r'\1(U32)pxTCB',s);put(f,s)
# Correct sample's word/byte mismatch in stack-watermark display.
f=V/'FreeRTOS/SEGGER_SYSVIEW_FreeRTOS.c'
edit(f,'uxTaskGetStackHighWaterMark((TaskHandle_t)_aTasks[n].xHandle);','uxTaskGetStackHighWaterMark((TaskHandle_t)_aTasks[n].xHandle) * sizeof(StackType_t);')
f=K/'portable/GCC/ARM_CM4F/port.c';s=f.read_text();start=s.index('void xPortSysTickHandler( void )\n{');end=s.index('/*------',start)
part=s[start:end].replace('portDISABLE_INTERRUPTS();','portDISABLE_INTERRUPTS();\n\ttraceISR_ENTER();')
part=part.replace('portENABLE_INTERRUPTS();','if (portNVIC_INT_CTRL_REG & portNVIC_PENDSVSET_BIT) { traceISR_EXIT_TO_SCHEDULER(); }\n\telse { traceISR_EXIT(); }\n\tportENABLE_INTERRUPTS();')
put(f,s[:start]+part+s[end:])
f=P/'Src/main.c';edit(f,'#include "app.h"','#include "app.h"\n#include "app_trace.h"')
edit(f,'  MX_FREERTOS_Init();','  AppTrace_Init();\n  MX_FREERTOS_Init();')
f=P/'Src/stm32f4xx_it.c';edit(f,'#include "app.h"','#include "app.h"\n#include "FreeRTOS.h"\n#include "app_trace.h"')
s=f.read_text()
for irq in ['DMA1_Stream5','DMA1_Stream6','TIM3','USART2','EXTI0']:
    begin=f'/* USER CODE BEGIN {irq}_IRQn 0 */'; end=f'/* USER CODE BEGIN {irq}_IRQn 1 */'
    if irq=='EXTI0':
        s=s.replace('uint32_t now = App_Now();','uint32_t now = App_Now();\n  AppTrace_IsrEnter();')
    else:s=s.replace(begin,begin+'\n  AppTrace_IsrEnter();')
    s=s.replace(end,end+'\n  AppTrace_IsrExit();')
put(f,s)
# The project enumerates Middlewares; add only include paths, not duplicate source entries.
f=P/'.cproject';s=f.read_text()
paths=['Config','SYSVIEW','SEGGER','RTT','FreeRTOS']
def inc(m):
    return m[0]+''.join(f'\n                                    <listOptionValue builtIn="false" value="../Middlewares/SEGGER/{p}"/>' for p in paths)
s=re.sub(r'<option[^>]+superClass="com\.st\.stm32cube\.ide\.mcu\.gnu\.managedbuild\.tool\.c\.compiler\.option\.includepaths"[^>]*>',inc,s)
put(f,s)
meta={name:subprocess.check_output(['git','rev-parse','HEAD'],cwd=W/'tools'/name,text=True).strip() for name in ['SystemView-source','RTT-source']}
put(W/'provenance/segger-sources.json',json.dumps(meta,indent=2))
print('V2 vendor, kernel, ISR and IDE integration prepared.')
