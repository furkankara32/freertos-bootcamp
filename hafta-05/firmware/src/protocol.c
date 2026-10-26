#include "protocol.h"
#include <string.h>
uint16_t frame_crc(const uint8_t *p, size_t n) {
    uint16_t c=0xffff;
    while(n--) { c^=(uint16_t)*p++<<8; for(unsigned i=0;i<8;i++) c=(c&0x8000)?(uint16_t)((c<<1)^0x1021):(uint16_t)(c<<1); }
    return c;
}
static uint32_t get32(const uint8_t *p) { return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24); }
static void put32(uint8_t *p,uint32_t v) { for(unsigned i=0;i<4;i++)p[i]=(uint8_t)(v>>(i*8)); }
void frame_encode(uint8_t out[FRAME_SIZE],const Message *m) {
    memset(out,0,FRAME_SIZE);out[0]='W';out[1]='5';out[2]=PROTOCOL_VERSION;out[3]=m->type;put32(out+4,m->seq);
    for(unsigned i=0;i<22;i++)put32(out+8+i*4,m->v[i]);
    uint16_t c=frame_crc(out,98);out[98]=(uint8_t)c;out[99]=(uint8_t)(c>>8);
}
int frame_feed(FrameParser *p,uint8_t b,Message *m) {
    p->data[p->used++]=b;
    if(p->used<FRAME_SIZE)return 0;
    uint16_t c=(uint16_t)p->data[98]|((uint16_t)p->data[99]<<8);
    if(p->data[0]=='W' && p->data[1]=='5' && p->data[2]==PROTOCOL_VERSION && frame_crc(p->data,98)==c) {
        m->type=p->data[3];m->seq=get32(p->data+4);for(unsigned i=0;i<22;i++)m->v[i]=get32(p->data+8+4*i);
        p->used=0;return 1;
    }
    memmove(p->data,p->data+1,--p->used);p->errors++;return 0;
}
