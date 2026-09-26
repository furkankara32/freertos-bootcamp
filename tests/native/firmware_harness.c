/* Executes production app.c against bounded queues and synchronous fake DMA.
 * This tests state/data flow, not RTOS timing or physical latency. */
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <setjmp.h>
#include "fake.h"
#include "../../firmware/Homework_001/Src/app.c"

Peripheral timer,uart,dma;
static DMA_HandleTypeDef dma_handle;
UART_HandleTypeDef huart2={&dma_handle,0};
TIM_HandleTypeDef htim5;
unsigned SystemCoreClock=168000000;
struct FakeQueue {unsigned cap,size,n,head;unsigned char data[16*80];};
static struct FakeQueue queues[8];static unsigned nq,notified,done,inject_idle;
static jmp_buf idle;
static char sent[1024];static unsigned sent_n,inject_tx;
static FILE *wire;
void Error_Handler(void){abort();}
int HAL_TIM_Base_Start(TIM_HandleTypeDef *p){(void)p;return HAL_OK;}
int HAL_UART_Receive_IT(UART_HandleTypeDef *p,uint8_t *b,unsigned n){(void)p;(void)b;(void)n;return HAL_OK;}
int HAL_UART_Transmit_DMA(UART_HandleTypeDef *p,uint8_t *b,unsigned n){
    assert(n==64);if(wire)assert(fwrite(b,1,n,wire)==n);
    else {assert(sent_n<sizeof(sent));sent[sent_n++]=b[0];}
    if(inject_tx){TxMsg m={.kind=BTN,.index=NO_RECORD};m.bytes[0]='I';assert(xQueueSend(btn_tx_q,&m,0));xTaskNotify(uart_task,TX_WORK,eSetBits);inject_tx=0;}
    timer.CNT+=APP_BAUD==460800?1400:5600;
    HAL_UART_TxCpltCallback(p);return HAL_OK;
}
int HAL_UART_AbortTransmit(UART_HandleTypeDef *p){(void)p;dma.CR=0;return HAL_OK;}
void HAL_NVIC_ClearPendingIRQ(int x){(void)x;}
void HAL_NVIC_SetPriority(int x,int y,int z){(void)x;(void)y;(void)z;}
void HAL_NVIC_EnableIRQ(int x){(void)x;}
unsigned HAL_RCC_GetPCLK1Freq(void){return 42000000;}
QueueHandle_t xQueueCreate(unsigned cap,unsigned size){assert(nq<8&&cap*size<=sizeof(queues[0].data));struct FakeQueue *q=&queues[nq++];q->cap=cap;q->size=size;return q;}
int xQueueSend(QueueHandle_t q,const void *p,unsigned wait){(void)wait;if(q->n==q->cap)return 0;memcpy(q->data+((q->head+q->n)%q->cap)*q->size,p,q->size);q->n++;return pdPASS;}
int xQueueSendFromISR(QueueHandle_t q,const void *p,int *wake){*wake=1;return xQueueSend(q,p,0);}
int xQueueReceive(QueueHandle_t q,void *p,unsigned wait){if(!q->n){if(wait==portMAX_DELAY)longjmp(idle,1);return 0;}memcpy(p,q->data+q->head*q->size,q->size);q->head=(q->head+1)%q->cap;q->n--;return pdPASS;}
unsigned uxQueueMessagesWaiting(QueueHandle_t q){return q->n;}
unsigned uxQueueMessagesWaitingFromISR(QueueHandle_t q){return q->n;}
unsigned xTaskGetTickCount(void){return timer.CNT/1000;}
TaskHandle_t xTaskGetCurrentTaskHandle(void){return (void *)1;}
int xTaskNotify(TaskHandle_t task,unsigned bits,int action){
    (void)action;
    if(task==control_task){
        if(bits&CTRL_DONE){assert(!btn_tx_q->n&&!tel_tx_q->n&&!tx_active);done++;}
    }else notified|=bits;
    return pdPASS;
}
int xTaskNotifyFromISR(TaskHandle_t t,unsigned b,int a,int *w){*w=1;return xTaskNotify(t,b,a);}
int xTaskNotifyWait(unsigned in,unsigned out,unsigned *bits,unsigned wait){
    notified&=~in;
    if(!notified&&wait==portMAX_DELAY){
        if(inject_idle){TxMsg m={.kind=TEL,.index=NO_RECORD};m.bytes[0]='W';assert(xQueueSend(tel_tx_q,&m,0));notified|=TX_WORK;inject_idle=0;}
        else longjmp(idle,1);
    }
    *bits=notified;notified&=~out;return *bits?pdPASS:0;
}
unsigned ulTaskNotifyValueClear(TaskHandle_t t,unsigned bits){(void)t;unsigned old=notified;notified&=~bits;return old;}
void vTaskDelay(unsigned ticks){timer.CNT+=ticks*1000;}
void vTaskDelayUntil(unsigned *last,unsigned period){*last+=period;timer.CNT=*last*1000;}
unsigned xPortGetMinimumEverFreeHeapSize(void){return 20000;}
unsigned uxTaskGetStackHighWaterMark(TaskHandle_t t){(void)t;return 400;}

int main(int argc,char **argv){
    assert(argc==2);App_Init();control_task=(void *)2;state=RUNNING;
    TxMsg a={.kind=TEL,.index=NO_RECORD},b={.kind=BTN,.index=NO_RECORD},bar={.kind=BARRIER,.index=NO_RECORD};
    a.bytes[0]='a';b.bytes[0]='B';assert(xQueueSend(tel_tx_q,&a,0));assert(xQueueSend(btn_tx_q,&b,0));
    a.bytes[0]='c';b.bytes[0]='D';assert(xQueueSend(tel_tx_q,&a,0));assert(xQueueSend(btn_tx_q,&b,0));assert(submit_control(&bar));
    inject_idle=1;if(!setjmp(idle))App_UartTask();
    assert(sent_n==5&&!memcmp(sent,"BDacW",5)&&done==1);
    /* Queue capacity and notification bits retained across DMA waits. */
    inject_tx=1;assert(xQueueSend(tel_tx_q,&a,0));assert(xQueueSend(tel_tx_q,&a,0));
    if(!setjmp(idle))App_UartTask();
    assert(sent_n==8&&!memcmp(sent+5,"cIc",3));
    for(unsigned i=0;i<8;i++)assert(xQueueSend(btn_tx_q,&b,0));
    assert(!xQueueSend(btn_tx_q,&b,0));
    accepting=1;timer.CNT=100000;App_ButtonIRQ(timer.CNT);
    if(!setjmp(idle))App_ButtonTask();
    assert(records[0].status==TX_DROP&&counters[BTX_DROP]==1&&records[0].mask==7);
    if(!setjmp(idle))App_UartTask();assert(sent_n==16);
    /* Slicing preserves all iterations and calculation state; delays excluded
     * from measured compute total (fake timer advances only on delay here). */
    iterations=101;slices=1;work_sink=7;uint32_t maximum;run_work(0,&maximum);uint32_t expected=work_sink;
    slices=5;work_sink=7;uint32_t before=timer.CNT;assert(run_work(1,&maximum)==0);
    assert(work_sink==expected&&timer.CNT-before==4000);
    /* Serialize a production firmware dump for the Python parser contract test. */
    reset_measurement();run_id=1;scenario=5;slices=APP_SLICED?5:1;iterations=5000;
    work_min=work_mean=work_max=5000;cal_slice_max=APP_SLICED?1000:5000;
    uart.BRR=APP_BAUD==460800?91:365;run_start=1000;run_stop=100000;
    record_count=1;records[0]=(Record){.id=1,.t={1000,1020,1040,1100,2500},.mask=31,.status=OK};
    counters[ACCEPTED]=1;counters[BQ_HWM]=counters[BTN_HWM]=1;
    memcpy(snapshot,counters,sizeof(snapshot));state=COMPLETE;
    wire=fopen(argv[1],"wb");assert(wire);
    assert(dump_line(NULL,"SYS,RTOSLAT,FW2-" APP_VARIANT ",PROTO3"));assert(dump_records());fclose(wire);
    puts("PASS: BTN priority, class FIFO, both-queue barrier, full queue, idle wake, firmware dump");return 0;
}
