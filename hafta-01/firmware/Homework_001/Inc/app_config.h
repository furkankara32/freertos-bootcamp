#ifndef APP_CONFIG_H
#define APP_CONFIG_H
/* Build profiles: Q=1, QW=2, QB=3, QWB=4. CubeIDE defaults to final V2. */
#ifndef APP_PROFILE
#define APP_PROFILE 4
#endif
#if APP_PROFILE == 1
#define APP_VARIANT "Q"
#elif APP_PROFILE == 2
#define APP_VARIANT "QW"
#elif APP_PROFILE == 3
#define APP_VARIANT "QB"
#elif APP_PROFILE == 4
#define APP_VARIANT "QWB"
#else
#error Invalid APP_PROFILE
#endif
#define APP_SLICED (APP_PROFILE == 2 || APP_PROFILE == 4)
#define APP_BAUD ((APP_PROFILE >= 3) ? 460800U : 115200U)
#define APP_DEADLINE_US 10000U
#endif
