#pragma once
#include <stdint.h>
#include <stddef.h>
#define FRAME_SIZE 100U
#define PROTOCOL_VERSION 1U
enum { CMD_HELLO=1, CMD_START, CMD_STOP, CMD_LOAD, CMD_WORK, CMD_SEQUENCE, CMD_TRACE, CMD_STATUS, CMD_DIAG };
enum { MSG_HELLO=128, MSG_ACK, MSG_RUN_START, MSG_LED, MSG_DONE, MSG_STATUS, MSG_ERROR, MSG_DIAG };
typedef struct { uint8_t type; uint32_t seq, v[22]; } Message;
typedef struct { uint8_t data[FRAME_SIZE]; size_t used; uint32_t errors; } FrameParser;
uint16_t frame_crc(const uint8_t *p, size_t n);
void frame_encode(uint8_t out[FRAME_SIZE], const Message *m);
int frame_feed(FrameParser *p, uint8_t b, Message *m);
