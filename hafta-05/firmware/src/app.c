#include "board.h"
#include "protocol.h"
#include "FreeRTOS.h"
#include "task.h"
#include "queue.h"
#include "event_groups.h"
#include "stream_buffer.h"
#include "app_trace.h"
#include "build_identity.h"
#include <string.h>
#define EV_COMMAND 1U
#define EV_STOP 2U
static StreamBufferHandle_t rx_stream,tx_stream;
static QueueHandle_t commands,results;
static EventGroupHandle_t events;
static TaskHandle_t report_handle;
static uint8_t rx_byte;
static volatile uint32_t rx_bytes,rx_drop,rx_error,report_drop,command_drop,crc_errors,load_frames;
static volatile uint32_t run_id,scenario=1,variant,active,poll_tx,tx_done=1,tx_frames,rx_high,rearm;
static uint32_t event_seq;
static volatile uint32_t work_sink;
static uint32_t work_per_ms=8000;
static const uint16_t led_pins[]={GPIO_PIN_12,GPIO_PIN_13,GPIO_PIN_14,GPIO_PIN_15};
static void emit(Message *m) {
 taskENTER_CRITICAL();m->seq=++event_seq;
 if(xQueueSend(results,m,0)==pdPASS)xTaskNotifyGiveIndexed(report_handle,1);else report_drop++;
 taskEXIT_CRITICAL();
}
static void response(uint8_t type,uint32_t id,uint32_t value) {
 Message m={.type=type};m.v[0]=run_id;m.v[1]=id;m.v[2]=value;m.v[3]=timer_us();emit(&m);
}
static void status(uint32_t id) {
 Message m={.type=MSG_STATUS};m.v[0]=run_id;m.v[1]=id;m.v[2]=active;
 m.v[3]=rx_bytes;m.v[4]=rx_drop;m.v[5]=rx_error;m.v[6]=crc_errors;m.v[7]=command_drop;m.v[8]=report_drop;
 m.v[9]=load_frames;m.v[10]=rx_high;m.v[11]=uxQueueMessagesWaiting(commands);m.v[12]=app_trace_bytes;
 m.v[13]=app_trace_dropped;m.v[14]=app_trace_complete;m.v[15]=app_trace_reason;m.v[16]=tx_frames;
 m.v[17]=scenario;m.v[18]=variant;m.v[19]=uxTaskGetStackHighWaterMark(NULL);m.v[20]=xPortGetFreeHeapSize();m.v[21]=timer_us();emit(&m);
}
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *u) {
 if(u!=&huart3)return;
 BaseType_t wake=pdFALSE;rx_bytes++;
 if(xStreamBufferSendFromISR(rx_stream,&rx_byte,1,&wake)!=1)rx_drop++;
 uint32_t used=xStreamBufferBytesAvailable(rx_stream);if(used>rx_high)rx_high=used;
 if(HAL_UART_Receive_IT(&huart3,&rx_byte,1)!=HAL_OK)rearm=1;
 portYIELD_FROM_ISR(wake);
}
void HAL_UART_ErrorCallback(UART_HandleTypeDef *u) {if(u==&huart3){rx_error++;rearm=1;}}
void app_uart_tx_irq(void) {
 BaseType_t wake=pdFALSE;uint8_t b;
 if((USART2->CR1 & USART_CR1_TXEIE) && (USART2->SR & USART_SR_TXE)) {
  if(xStreamBufferReceiveFromISR(tx_stream,&b,1,&wake)==1)USART2->DR=b;
  else {USART2->CR1 &= ~USART_CR1_TXEIE;USART2->CR1|=USART_CR1_TCIE;}
 }
 if((USART2->CR1 & USART_CR1_TCIE) && (USART2->SR & USART_SR_TC)) {
  USART2->CR1 &= ~USART_CR1_TCIE;tx_done=1;vTaskNotifyGiveIndexedFromISR(report_handle,2,&wake);
 }
 portYIELD_FROM_ISR(wake);
}
static void transmit(const uint8_t *data) {
 configASSERT(xStreamBufferSend(tx_stream,data,FRAME_SIZE,0)==FRAME_SIZE);
 tx_done=0;AppTrace_Event(TR_TX_BEGIN,run_id,tx_frames,0);
 if(poll_tx) {
  uint8_t b;
  while(xStreamBufferReceive(tx_stream,&b,1,0)==1){while(!(USART2->SR & USART_SR_TXE)){} USART2->DR=b;}
  while(!(USART2->SR & USART_SR_TC)){} tx_done=1;
 } else {
  (void)ulTaskNotifyTakeIndexed(2,pdTRUE,0);USART2->CR1|=USART_CR1_TXEIE;
  while(!tx_done)ulTaskNotifyTakeIndexed(2,pdTRUE,portMAX_DELAY);
 }
 tx_frames++;AppTrace_Event(TR_TX_END,run_id,tx_frames,0);
}
static void report_task(void *arg) {
 (void)arg;Message m;uint8_t wire[FRAME_SIZE];
 for(;;){ulTaskNotifyTakeIndexed(1,pdFALSE,portMAX_DELAY);configASSERT(xQueueReceive(results,&m,0)==pdPASS);
  uint32_t count=m.type==MSG_DIAG?m.v[2]:1;if(count>20)count=20;
  for(uint32_t i=0;i<count;i++){if(m.type==MSG_DIAG)m.v[21]=i;frame_encode(wire,&m);transmit(wire);}
 }
}
static void cpu_work(uint32_t amount) {
 for(uint32_t i=0;i<amount*work_per_ms;i++){work_sink=work_sink*1664525U+1013904223U;__asm volatile("" ::: "memory");}
}
static void parser_task(void *arg) {
 (void)arg;FrameParser p={0};Message m;uint8_t bytes[128];uint32_t last=0;
 configASSERT(HAL_UART_Receive_IT(&huart3,&rx_byte,1)==HAL_OK);
 for(;;){
  if(rearm){HAL_UART_AbortReceive(&huart3);rearm=HAL_UART_Receive_IT(&huart3,&rx_byte,1)!=HAL_OK;}
  size_t n=xStreamBufferReceive(rx_stream,bytes,sizeof bytes,pdMS_TO_TICKS(20));
  if(!n){if(p.used && (uint32_t)(timer_us()-last)>100000U){p.used=0;p.errors++;crc_errors=p.errors;}continue;}
  last=timer_us();
  for(size_t i=0;i<n;i++){
   if(!frame_feed(&p,bytes[i],&m)){crc_errors=p.errors;continue;}
   if(m.type==CMD_LOAD){load_frames++;continue;}
   AppTrace_Event(TR_FRAME,run_id,m.seq,m.type);
   if(m.type==CMD_HELLO){Message h={.type=MSG_HELLO};h.v[0]=0xF4070005;h.v[1]=1;h.v[2]=115200;h.v[3]=timer_us();memcpy(&h.v[4],APP_BUILD_ID,32);emit(&h);continue;}
   if(m.type==CMD_STATUS){status(m.seq);continue;}
   if(m.type==CMD_STOP){xEventGroupSetBits(events,EV_STOP);response(MSG_ACK,m.seq,0);continue;}
   if(m.type==CMD_TRACE){AppTrace_Start(m.v[0]>2000?2000:m.v[0]);AppTrace_Event(TR_RUN,run_id,scenario,variant);response(MSG_ACK,m.seq,0);continue;}
   if(m.type==CMD_DIAG){Message d={.type=MSG_DIAG};d.v[0]=run_id;d.v[2]=20;emit(&d);continue;}
   if(m.type==CMD_WORK){uint32_t amount=m.v[0]>200?200:m.v[0],begin=timer_us();AppTrace_Event(TR_WORK_BEGIN,run_id,m.seq,amount);
    if(scenario==3 && variant==1){for(uint32_t j=0;j<amount;j+=5){cpu_work(amount-j<5?amount-j:5);vTaskDelay(1);}}else cpu_work(amount);
    AppTrace_Event(TR_WORK_END,run_id,m.seq,timer_us()-begin);response(MSG_ACK,m.seq,timer_us()-begin);continue;}
   if(m.type==CMD_START || m.type==CMD_SEQUENCE){
    if(m.v[3]<50 || m.v[3]>5000 || m.v[4]<1 || m.v[4]>100){response(MSG_ERROR,m.seq,3);continue;}
    if(m.type==CMD_START && (m.v[1]<1 || m.v[1]>4 || m.v[2]>(m.v[1]==1?0U:m.v[1]==2?2U:1U))){response(MSG_ERROR,m.seq,3);continue;}
    if(m.type==CMD_START && (active || uxQueueMessagesWaiting(commands))){response(MSG_ERROR,m.seq,4);continue;}
    if(xQueueSend(commands,&m,0)==pdPASS){xEventGroupSetBits(events,EV_COMMAND);AppTrace_Event(TR_EVENT,run_id,m.seq,0);}
    else{command_drop++;response(MSG_ERROR,m.seq,1);}
   }else response(MSG_ERROR,m.seq,2);
  }
 }
}
static void led(uint32_t color){uint32_t set=color<4?led_pins[color]:0;GPIOD->BSRR=((uint32_t)((GPIO_PIN_12|GPIO_PIN_13|GPIO_PIN_14|GPIO_PIN_15)&~set)<<16)|set;}
static void execute_task(void *arg) {
 (void)arg;Message c;uint32_t period=1000000,remaining=0,color=0,planned=0,on=0,current_cmd=0;BaseType_t event_credit=pdFALSE;
 for(;;){
  uint32_t now=timer_us();TickType_t timeout=pdMS_TO_TICKS(20);
  if(active){int32_t left=(int32_t)(planned-now);timeout=left<=0?0:pdMS_TO_TICKS(((uint32_t)left+999)/1000);}
  if(!active && uxQueueMessagesWaiting(commands) && !(scenario==4 && variant==0))timeout=0;
  EventBits_t bits=xEventGroupWaitBits(events,EV_COMMAND|EV_STOP,pdTRUE,pdFALSE,timeout);
  if(bits&EV_COMMAND)event_credit=pdTRUE;
  if(bits&EV_STOP){active=0;remaining=0;led(4);xQueueReset(commands);AppTrace_Event(TR_DONE,run_id,0,0);AppTrace_Stop();response(MSG_DONE,0,0);event_credit=pdFALSE;}
  now=timer_us();
  if(active && (int32_t)(now-planned)>=0){
   uint32_t old=color;remaining--;color=remaining?(color+1)%4:4;led(color);now=timer_us();
   Message out={.type=MSG_LED};out.v[0]=run_id;out.v[1]=current_cmd;out.v[2]=old;out.v[3]=color;out.v[4]=planned;out.v[5]=now;out.v[6]=on;out.v[7]=now-on;out.v[8]=now-planned;out.v[9]=period;emit(&out);
   AppTrace_Event(TR_LED,run_id,old,now-planned);on=now;do{planned+=period;}while((int32_t)(now-planned)>=0);
   if(!remaining){active=0;response(MSG_DONE,current_cmd,0);}
  }
  if(!active && (event_credit || !(scenario==4 && variant==0))){
   if(xQueueReceive(commands,&c,0)==pdPASS){event_credit=pdFALSE;
    if(c.type==CMD_START){
     if(c.v[1]<1 || c.v[1]>4 || c.v[2]>2){response(MSG_ERROR,c.seq,3);continue;}
     while(uxQueueMessagesWaiting(results) || !tx_done)vTaskDelay(1);
     run_id=c.v[0];scenario=c.v[1];variant=c.v[2];poll_tx=scenario==2 && variant!=2;
     vTaskPrioritySet(report_handle,(scenario==2 && variant!=1)?5:2);
     if(c.v[5]){AppTrace_Start(c.v[5]>2000?2000:c.v[5]);AppTrace_Event(TR_RUN,run_id,scenario,variant);}
     response(MSG_RUN_START,c.seq,scenario);
    }
    period=c.v[3]*1000U;if(period<50000 || period>5000000)period=1000000;
    remaining=c.v[4]*4;if(!remaining || remaining>400)remaining=12;
    current_cmd=c.seq;color=0;led(color);on=timer_us();planned=on+period;active=1;
    Message out={.type=MSG_LED};out.v[0]=run_id;out.v[1]=current_cmd;out.v[2]=4;out.v[3]=0;out.v[5]=on;out.v[9]=period;emit(&out);AppTrace_Event(TR_EXECUTE,run_id,c.seq,period);
   }
  }
 }
}
void app_init(void){
 uint32_t begin=timer_us();cpu_work(10);uint32_t elapsed=timer_us()-begin;
 if(elapsed)work_per_ms=(uint32_t)((uint64_t)80000*1000/elapsed);
 rx_stream=xStreamBufferCreate(4096,64);tx_stream=xStreamBufferCreate(512,1);
 commands=xQueueCreate(8,sizeof(Message));results=xQueueCreate(64,sizeof(Message));events=xEventGroupCreate();
 configASSERT(rx_stream && tx_stream && commands && results && events);AppTrace_NameQueue(commands);
 configASSERT(xTaskCreate(report_task,"Report",768,NULL,2,&report_handle)==pdPASS);
 configASSERT(xTaskCreate(execute_task,"Execute",768,NULL,3,NULL)==pdPASS);
 configASSERT(xTaskCreate(parser_task,"Parser",1024,NULL,4,NULL)==pdPASS);
}
