/* API verbosity off; scheduler and application trace remain enabled. */
#undef traceENTER_xQueueGenericReset
#define traceENTER_xQueueGenericReset(xQueue, xNewQueue) ((void)0)
#undef traceENTER_xQueueGenericCreateStatic
#define traceENTER_xQueueGenericCreateStatic(uxQueueLength, uxItemSize, pucQueueStorage, pxStaticQueue, ucQueueType) ((void)0)
#undef traceENTER_xQueueGenericCreate
#define traceENTER_xQueueGenericCreate(uxQueueLength, uxItemSize, ucQueueType) ((void)0)
#undef traceENTER_xQueueCreateMutex
#define traceENTER_xQueueCreateMutex(ucQueueType) ((void)0)
#undef traceENTER_xQueueCreateMutexStatic
#define traceENTER_xQueueCreateMutexStatic(ucQueueType, pxStaticQueue) ((void)0)
#undef traceENTER_xQueueGetMutexHolder
#define traceENTER_xQueueGetMutexHolder(xSemaphore) ((void)0)
#undef traceENTER_xQueueGetMutexHolderFromISR
#define traceENTER_xQueueGetMutexHolderFromISR(xSemaphore) ((void)0)
#undef traceENTER_xQueueGiveMutexRecursive
#define traceENTER_xQueueGiveMutexRecursive(xMutex) ((void)0)
#undef traceENTER_xQueueTakeMutexRecursive
#define traceENTER_xQueueTakeMutexRecursive(xMutex, xTicksToWait) ((void)0)
#undef traceENTER_xQueueCreateCountingSemaphoreStatic
#define traceENTER_xQueueCreateCountingSemaphoreStatic(uxMaxCount, uxInitialCount, pxStaticQueue) ((void)0)
#undef traceENTER_xQueueCreateCountingSemaphore
#define traceENTER_xQueueCreateCountingSemaphore(uxMaxCount, uxInitialCount) ((void)0)
#undef traceENTER_xQueueGenericSend
#define traceENTER_xQueueGenericSend(xQueue, pvItemToQueue, xTicksToWait, xCopyPosition) ((void)0)
#undef traceENTER_xQueueGenericSendFromISR
#define traceENTER_xQueueGenericSendFromISR(xQueue, pvItemToQueue, pxHigherPriorityTaskWoken, xCopyPosition) ((void)0)
#undef traceENTER_xQueueGiveFromISR
#define traceENTER_xQueueGiveFromISR(xQueue, pxHigherPriorityTaskWoken) ((void)0)
#undef traceENTER_xQueueReceive
#define traceENTER_xQueueReceive(xQueue, pvBuffer, xTicksToWait) ((void)0)
#undef traceENTER_xQueueSemaphoreTake
#define traceENTER_xQueueSemaphoreTake(xQueue, xTicksToWait) ((void)0)
#undef traceENTER_xQueuePeek
#define traceENTER_xQueuePeek(xQueue, pvBuffer, xTicksToWait) ((void)0)
#undef traceENTER_xQueueReceiveFromISR
#define traceENTER_xQueueReceiveFromISR(xQueue, pvBuffer, pxHigherPriorityTaskWoken) ((void)0)
#undef traceENTER_xQueuePeekFromISR
#define traceENTER_xQueuePeekFromISR(xQueue, pvBuffer) ((void)0)
#undef traceENTER_uxQueueMessagesWaiting
#define traceENTER_uxQueueMessagesWaiting(xQueue) ((void)0)
#undef traceENTER_uxQueueSpacesAvailable
#define traceENTER_uxQueueSpacesAvailable(xQueue) ((void)0)
#undef traceENTER_uxQueueMessagesWaitingFromISR
#define traceENTER_uxQueueMessagesWaitingFromISR(xQueue) ((void)0)
#undef traceENTER_vQueueDelete
#define traceENTER_vQueueDelete(xQueue) ((void)0)
#undef traceENTER_uxQueueGetQueueNumber
#define traceENTER_uxQueueGetQueueNumber(xQueue) ((void)0)
#undef traceENTER_vQueueSetQueueNumber
#define traceENTER_vQueueSetQueueNumber(xQueue, uxQueueNumber) ((void)0)
#undef traceENTER_ucQueueGetQueueType
#define traceENTER_ucQueueGetQueueType(xQueue) ((void)0)
#undef traceENTER_xQueueIsQueueEmptyFromISR
#define traceENTER_xQueueIsQueueEmptyFromISR(xQueue) ((void)0)
#undef traceENTER_xQueueIsQueueFullFromISR
#define traceENTER_xQueueIsQueueFullFromISR(xQueue) ((void)0)
#undef traceENTER_xQueueCRSend
#define traceENTER_xQueueCRSend(xQueue, pvItemToQueue, xTicksToWait) ((void)0)
#undef traceENTER_xQueueCRReceive
#define traceENTER_xQueueCRReceive(xQueue, pvBuffer, xTicksToWait) ((void)0)
#undef traceENTER_xQueueCRSendFromISR
#define traceENTER_xQueueCRSendFromISR(xQueue, pvItemToQueue, xCoRoutinePreviouslyWoken) ((void)0)
#undef traceENTER_xQueueCRReceiveFromISR
#define traceENTER_xQueueCRReceiveFromISR(xQueue, pvBuffer, pxCoRoutineWoken) ((void)0)
#undef traceENTER_vQueueAddToRegistry
#define traceENTER_vQueueAddToRegistry(xQueue, pcQueueName) ((void)0)
#undef traceENTER_pcQueueGetName
#define traceENTER_pcQueueGetName(xQueue) ((void)0)
#undef traceENTER_vQueueUnregisterQueue
#define traceENTER_vQueueUnregisterQueue(xQueue) ((void)0)
#undef traceENTER_vQueueWaitForMessageRestricted
#define traceENTER_vQueueWaitForMessageRestricted(xQueue, xTicksToWait, xWaitIndefinitely) ((void)0)
#undef traceENTER_xQueueCreateSet
#define traceENTER_xQueueCreateSet(uxEventQueueLength) ((void)0)
#undef traceENTER_xQueueAddToSet
#define traceENTER_xQueueAddToSet(xQueueOrSemaphore, xQueueSet) ((void)0)
#undef traceENTER_xQueueRemoveFromSet
#define traceENTER_xQueueRemoveFromSet(xQueueOrSemaphore, xQueueSet) ((void)0)
#undef traceENTER_xQueueSelectFromSet
#define traceENTER_xQueueSelectFromSet(xQueueSet, xTicksToWait) ((void)0)
#undef traceENTER_xQueueSelectFromSetFromISR
#define traceENTER_xQueueSelectFromSetFromISR(xQueueSet) ((void)0)
#undef traceENTER_xTaskCreateStatic
#define traceENTER_xTaskCreateStatic(pxTaskCode, pcName, ulStackDepth, pvParameters, uxPriority, puxStackBuffer, pxTaskBuffer) ((void)0)
#undef traceENTER_xTaskCreateRestrictedStatic
#define traceENTER_xTaskCreateRestrictedStatic(pxTaskDefinition, pxCreatedTask) ((void)0)
#undef traceENTER_xTaskCreateRestricted
#define traceENTER_xTaskCreateRestricted(pxTaskDefinition, pxCreatedTask) ((void)0)
#undef traceENTER_xTaskCreate
#define traceENTER_xTaskCreate(pxTaskCode, pcName, usStackDepth, pvParameters, uxPriority, pxCreatedTask) ((void)0)
#undef traceENTER_vTaskDelete
#define traceENTER_vTaskDelete(xTaskToDelete) ((void)0)
#undef traceENTER_xTaskDelayUntil
#define traceENTER_xTaskDelayUntil(pxPreviousWakeTime, xTimeIncrement) ((void)0)
#undef traceENTER_vTaskDelay
#define traceENTER_vTaskDelay(xTicksToDelay) ((void)0)
#undef traceENTER_eTaskGetState
#define traceENTER_eTaskGetState(xTask) ((void)0)
#undef traceENTER_uxTaskPriorityGet
#define traceENTER_uxTaskPriorityGet(xTask) ((void)0)
#undef traceENTER_uxTaskPriorityGetFromISR
#define traceENTER_uxTaskPriorityGetFromISR(xTask) ((void)0)
#undef traceENTER_vTaskPrioritySet
#define traceENTER_vTaskPrioritySet(xTask, uxNewPriority) ((void)0)
#undef traceENTER_vTaskSuspend
#define traceENTER_vTaskSuspend(xTaskToSuspend) ((void)0)
#undef traceENTER_vTaskResume
#define traceENTER_vTaskResume(xTaskToResume) ((void)0)
#undef traceENTER_xTaskResumeFromISR
#define traceENTER_xTaskResumeFromISR(xTaskToResume) ((void)0)
#undef traceENTER_vTaskStartScheduler
#define traceENTER_vTaskStartScheduler() ((void)0)
#undef traceENTER_vTaskEndScheduler
#define traceENTER_vTaskEndScheduler() ((void)0)
#undef traceENTER_vTaskSuspendAll
#define traceENTER_vTaskSuspendAll() ((void)0)
#undef traceENTER_xTaskResumeAll
#define traceENTER_xTaskResumeAll() ((void)0)
#undef traceENTER_xTaskGetTickCount
#define traceENTER_xTaskGetTickCount() ((void)0)
#undef traceENTER_xTaskGetTickCountFromISR
#define traceENTER_xTaskGetTickCountFromISR() ((void)0)
#undef traceENTER_uxTaskGetNumberOfTasks
#define traceENTER_uxTaskGetNumberOfTasks() ((void)0)
#undef traceENTER_pcTaskGetName
#define traceENTER_pcTaskGetName(xTaskToQuery) ((void)0)
#undef traceENTER_xTaskGetHandle
#define traceENTER_xTaskGetHandle(pcNameToQuery) ((void)0)
#undef traceENTER_uxTaskGetSystemState
#define traceENTER_uxTaskGetSystemState(pxTaskStatusArray, uxArraySize, pulTotalRunTime) ((void)0)
#undef traceENTER_xTaskGetIdleTaskHandle
#define traceENTER_xTaskGetIdleTaskHandle() ((void)0)
#undef traceENTER_vTaskStepTick
#define traceENTER_vTaskStepTick(xTicksToJump) ((void)0)
#undef traceENTER_xTaskCatchUpTicks
#define traceENTER_xTaskCatchUpTicks(xTicksToCatchUp) ((void)0)
#undef traceENTER_xTaskAbortDelay
#define traceENTER_xTaskAbortDelay(xTask) ((void)0)
#undef traceENTER_xTaskIncrementTick
#define traceENTER_xTaskIncrementTick() ((void)0)
#undef traceENTER_vTaskSetApplicationTaskTag
#define traceENTER_vTaskSetApplicationTaskTag(xTask, pxHookFunction) ((void)0)
#undef traceENTER_xTaskGetApplicationTaskTag
#define traceENTER_xTaskGetApplicationTaskTag(xTask) ((void)0)
#undef traceENTER_xTaskGetApplicationTaskTagFromISR
#define traceENTER_xTaskGetApplicationTaskTagFromISR(xTask) ((void)0)
#undef traceENTER_xTaskCallApplicationTaskHook
#define traceENTER_xTaskCallApplicationTaskHook(xTask, pvParameter) ((void)0)
#undef traceENTER_vTaskPlaceOnEventList
#define traceENTER_vTaskPlaceOnEventList(pxEventList, xTicksToWait) ((void)0)
#undef traceENTER_vTaskPlaceOnUnorderedEventList
#define traceENTER_vTaskPlaceOnUnorderedEventList(pxEventList, xItemValue, xTicksToWait) ((void)0)
#undef traceENTER_vTaskPlaceOnEventListRestricted
#define traceENTER_vTaskPlaceOnEventListRestricted(pxEventList, xTicksToWait, xWaitIndefinitely) ((void)0)
#undef traceENTER_xTaskRemoveFromEventList
#define traceENTER_xTaskRemoveFromEventList(pxEventList) ((void)0)
#undef traceENTER_vTaskRemoveFromUnorderedEventList
#define traceENTER_vTaskRemoveFromUnorderedEventList(pxEventListItem, xItemValue) ((void)0)
#undef traceENTER_vTaskSetTimeOutState
#define traceENTER_vTaskSetTimeOutState(pxTimeOut) ((void)0)
#undef traceENTER_vTaskInternalSetTimeOutState
#define traceENTER_vTaskInternalSetTimeOutState(pxTimeOut) ((void)0)
#undef traceENTER_xTaskCheckForTimeOut
#define traceENTER_xTaskCheckForTimeOut(pxTimeOut, pxTicksToWait) ((void)0)
#undef traceENTER_vTaskMissedYield
#define traceENTER_vTaskMissedYield() ((void)0)
#undef traceENTER_uxTaskGetTaskNumber
#define traceENTER_uxTaskGetTaskNumber(xTask) ((void)0)
#undef traceENTER_vTaskSetTaskNumber
#define traceENTER_vTaskSetTaskNumber(xTask, uxHandle) ((void)0)
#undef traceENTER_eTaskConfirmSleepModeStatus
#define traceENTER_eTaskConfirmSleepModeStatus() ((void)0)
#undef traceENTER_vTaskSetThreadLocalStoragePointer
#define traceENTER_vTaskSetThreadLocalStoragePointer(xTaskToSet, xIndex, pvValue) ((void)0)
#undef traceENTER_pvTaskGetThreadLocalStoragePointer
#define traceENTER_pvTaskGetThreadLocalStoragePointer(xTaskToQuery, xIndex) ((void)0)
#undef traceENTER_vTaskAllocateMPURegions
#define traceENTER_vTaskAllocateMPURegions(xTaskToModify, xRegions) ((void)0)
#undef traceENTER_vTaskGetInfo
#define traceENTER_vTaskGetInfo(xTask, pxTaskStatus, xGetFreeStackSpace, eState) ((void)0)
#undef traceENTER_uxTaskGetStackHighWaterMark2
#define traceENTER_uxTaskGetStackHighWaterMark2(xTask) ((void)0)
#undef traceENTER_uxTaskGetStackHighWaterMark
#define traceENTER_uxTaskGetStackHighWaterMark(xTask) ((void)0)
#undef traceENTER_pxTaskGetStackStart
#define traceENTER_pxTaskGetStackStart(xTask) ((void)0)
#undef traceENTER_xTaskGetCurrentTaskHandle
#define traceENTER_xTaskGetCurrentTaskHandle() ((void)0)
#undef traceENTER_xTaskGetSchedulerState
#define traceENTER_xTaskGetSchedulerState() ((void)0)
#undef traceENTER_xTaskPriorityInherit
#define traceENTER_xTaskPriorityInherit(pxMutexHolder) ((void)0)
#undef traceENTER_xTaskPriorityDisinherit
#define traceENTER_xTaskPriorityDisinherit(pxMutexHolder) ((void)0)
#undef traceENTER_vTaskPriorityDisinheritAfterTimeout
#define traceENTER_vTaskPriorityDisinheritAfterTimeout(pxMutexHolder, uxHighestPriorityWaitingTask) ((void)0)
#undef traceENTER_vTaskEnterCritical
#define traceENTER_vTaskEnterCritical() ((void)0)
#undef traceENTER_vTaskExitCritical
#define traceENTER_vTaskExitCritical() ((void)0)
#undef traceENTER_vTaskList
#define traceENTER_vTaskList(pcWriteBuffer) ((void)0)
#undef traceENTER_vTaskGetRunTimeStats
#define traceENTER_vTaskGetRunTimeStats(pcWriteBuffer) ((void)0)
#undef traceENTER_uxTaskResetEventItemValue
#define traceENTER_uxTaskResetEventItemValue() ((void)0)
#undef traceENTER_pvTaskIncrementMutexHeldCount
#define traceENTER_pvTaskIncrementMutexHeldCount() ((void)0)
#undef traceENTER_ulTaskGenericNotifyTake
#define traceENTER_ulTaskGenericNotifyTake(uxIndexToWaitOn, xClearCountOnExit, xTicksToWait) ((void)0)
#undef traceENTER_xTaskGenericNotifyWait
#define traceENTER_xTaskGenericNotifyWait(uxIndexToWaitOn, ulBitsToClearOnEntry, ulBitsToClearOnExit, pulNotificationValue, xTicksToWait) ((void)0)
#undef traceENTER_xTaskGenericNotify
#define traceENTER_xTaskGenericNotify(xTaskToNotify, uxIndexToNotify, ulValue, eAction, pulPreviousNotificationValue) ((void)0)
#undef traceENTER_xTaskGenericNotifyFromISR
#define traceENTER_xTaskGenericNotifyFromISR(xTaskToNotify, uxIndexToNotify, ulValue, eAction, pulPreviousNotificationValue, pxHigherPriorityTaskWoken) ((void)0)
#undef traceENTER_vTaskGenericNotifyGiveFromISR
#define traceENTER_vTaskGenericNotifyGiveFromISR(xTaskToNotify, uxIndexToNotify, pxHigherPriorityTaskWoken) ((void)0)
#undef traceENTER_xTaskGenericNotifyStateClear
#define traceENTER_xTaskGenericNotifyStateClear(xTask, uxIndexToClear) ((void)0)
#undef traceENTER_ulTaskGenericNotifyValueClear
#define traceENTER_ulTaskGenericNotifyValueClear(xTask, uxIndexToClear, ulBitsToClear) ((void)0)
#undef traceENTER_ulTaskGetIdleRunTimeCounter
#define traceENTER_ulTaskGetIdleRunTimeCounter() ((void)0)
#undef traceENTER_ulTaskGetIdleRunTimePercent
#define traceENTER_ulTaskGetIdleRunTimePercent() ((void)0)
#undef traceENTER_vTaskCoreAffinitySet
#define traceENTER_vTaskCoreAffinitySet(xTask, uxCoreAffinityMask) ((void)0)
#undef traceENTER_vTaskCoreAffinityGet
#define traceENTER_vTaskCoreAffinityGet(xTask) ((void)0)
#undef traceENTER_vTaskPreemptionDisable
#define traceENTER_vTaskPreemptionDisable(xTask) ((void)0)
#undef traceENTER_vTaskPreemptionEnable
#define traceENTER_vTaskPreemptionEnable(xTask) ((void)0)
#undef traceENTER_vTaskYieldWithinAPI
#define traceENTER_vTaskYieldWithinAPI() ((void)0)
#undef traceENTER_vTaskEnterCriticalFromISR
#define traceENTER_vTaskEnterCriticalFromISR() ((void)0)
#undef traceENTER_vTaskExitCriticalFromISR
#define traceENTER_vTaskExitCriticalFromISR(uxSavedInterruptStatus) ((void)0)
#undef traceENTER_ulTaskGetRunTimeCounter
#define traceENTER_ulTaskGetRunTimeCounter(xTask) ((void)0)
#undef traceENTER_xTimerCreateTimerTask
#define traceENTER_xTimerCreateTimerTask() ((void)0)
#undef traceENTER_xTimerCreate
#define traceENTER_xTimerCreate(pcTimerName, xTimerPeriodInTicks, xAutoReload, pvTimerID, pxCallbackFunction) ((void)0)
#undef traceENTER_xTimerCreateStatic
#define traceENTER_xTimerCreateStatic(pcTimerName, xTimerPeriodInTicks, xAutoReload, pvTimerID, pxCallbackFunction, pxTimerBuffer) ((void)0)
#undef traceENTER_xTimerGenericCommand
#define traceENTER_xTimerGenericCommand(xTimer, xCommandID, xOptionalValue, pxHigherPriorityTaskWoken, xTicksToWait) ((void)0)
#undef traceENTER_xTimerGenericCommandFromTask
#define traceENTER_xTimerGenericCommandFromTask(xTimer, xCommandID, xOptionalValue, pxHigherPriorityTaskWoken, xTicksToWait) ((void)0)
#undef traceENTER_xTimerGenericCommandFromISR
#define traceENTER_xTimerGenericCommandFromISR(xTimer, xCommandID, xOptionalValue, pxHigherPriorityTaskWoken, xTicksToWait) ((void)0)
#undef traceENTER_xTimerGetTimerDaemonTaskHandle
#define traceENTER_xTimerGetTimerDaemonTaskHandle() ((void)0)
#undef traceENTER_xTimerGetPeriod
#define traceENTER_xTimerGetPeriod(xTimer) ((void)0)
#undef traceENTER_vTimerSetReloadMode
#define traceENTER_vTimerSetReloadMode(xTimer, xAutoReload) ((void)0)
#undef traceENTER_xTimerGetReloadMode
#define traceENTER_xTimerGetReloadMode(xTimer) ((void)0)
#undef traceENTER_xTimerGetExpiryTime
#define traceENTER_xTimerGetExpiryTime(xTimer) ((void)0)
#undef traceENTER_pcTimerGetName
#define traceENTER_pcTimerGetName(xTimer) ((void)0)
#undef traceENTER_xTimerIsTimerActive
#define traceENTER_xTimerIsTimerActive(xTimer) ((void)0)
#undef traceENTER_pvTimerGetTimerID
#define traceENTER_pvTimerGetTimerID(xTimer) ((void)0)
#undef traceENTER_vTimerSetTimerID
#define traceENTER_vTimerSetTimerID(xTimer, pvNewID) ((void)0)
#undef traceENTER_xTimerPendFunctionCallFromISR
#define traceENTER_xTimerPendFunctionCallFromISR(xFunctionToPend, pvParameter1, ulParameter2, pxHigherPriorityTaskWoken) ((void)0)
#undef traceENTER_xTimerPendFunctionCall
#define traceENTER_xTimerPendFunctionCall(xFunctionToPend, pvParameter1, ulParameter2, xTicksToWait) ((void)0)
#undef traceENTER_uxTimerGetTimerNumber
#define traceENTER_uxTimerGetTimerNumber(xTimer) ((void)0)
#undef traceENTER_vTimerSetTimerNumber
#define traceENTER_vTimerSetTimerNumber(xTimer, uxTimerNumber) ((void)0)
#undef traceENTER_vListInitialise
#define traceENTER_vListInitialise(pxList) ((void)0)
#undef traceENTER_vListInitialiseItem
#define traceENTER_vListInitialiseItem(pxItem) ((void)0)
#undef traceENTER_vListInsertEnd
#define traceENTER_vListInsertEnd(pxList, pxNewListItem) ((void)0)
#undef traceENTER_vListInsert
#define traceENTER_vListInsert(pxList, pxNewListItem) ((void)0)
#undef traceENTER_uxListRemove
#define traceENTER_uxListRemove(pxItemToRemove) ((void)0)
#undef traceENTER_xCoRoutineCreate
#define traceENTER_xCoRoutineCreate(pxCoRoutineCode, uxPriority, uxIndex) ((void)0)
#undef traceENTER_vCoRoutineAddToDelayedList
#define traceENTER_vCoRoutineAddToDelayedList(xTicksToDelay, pxEventList) ((void)0)
#undef traceENTER_vCoRoutineSchedule
#define traceENTER_vCoRoutineSchedule() ((void)0)
#undef traceENTER_xCoRoutineRemoveFromEventList
#define traceENTER_xCoRoutineRemoveFromEventList(pxEventList) ((void)0)
#undef traceENTER_xEventGroupCreateStatic
#define traceENTER_xEventGroupCreateStatic(pxEventGroupBuffer) ((void)0)
#undef traceENTER_xEventGroupCreate
#define traceENTER_xEventGroupCreate() ((void)0)
#undef traceENTER_xEventGroupSync
#define traceENTER_xEventGroupSync(xEventGroup, uxBitsToSet, uxBitsToWaitFor, xTicksToWait) ((void)0)
#undef traceENTER_xEventGroupWaitBits
#define traceENTER_xEventGroupWaitBits(xEventGroup, uxBitsToWaitFor, xClearOnExit, xWaitForAllBits, xTicksToWait) ((void)0)
#undef traceENTER_xEventGroupClearBits
#define traceENTER_xEventGroupClearBits(xEventGroup, uxBitsToClear) ((void)0)
#undef traceENTER_xEventGroupClearBitsFromISR
#define traceENTER_xEventGroupClearBitsFromISR(xEventGroup, uxBitsToClear) ((void)0)
#undef traceENTER_xEventGroupGetBitsFromISR
#define traceENTER_xEventGroupGetBitsFromISR(xEventGroup) ((void)0)
#undef traceENTER_xEventGroupSetBits
#define traceENTER_xEventGroupSetBits(xEventGroup, uxBitsToSet) ((void)0)
#undef traceENTER_vEventGroupDelete
#define traceENTER_vEventGroupDelete(xEventGroup) ((void)0)
#undef traceENTER_vEventGroupSetBitsCallback
#define traceENTER_vEventGroupSetBitsCallback(pvEventGroup, ulBitsToSet) ((void)0)
#undef traceENTER_vEventGroupClearBitsCallback
#define traceENTER_vEventGroupClearBitsCallback(pvEventGroup, ulBitsToClear) ((void)0)
#undef traceENTER_xEventGroupSetBitsFromISR
#define traceENTER_xEventGroupSetBitsFromISR(xEventGroup, uxBitsToSet, pxHigherPriorityTaskWoken) ((void)0)
#undef traceENTER_uxEventGroupGetNumber
#define traceENTER_uxEventGroupGetNumber(xEventGroup) ((void)0)
#undef traceENTER_vEventGroupSetNumber
#define traceENTER_vEventGroupSetNumber(xEventGroup, uxEventGroupNumber) ((void)0)
#undef traceENTER_xStreamBufferGenericCreate
#define traceENTER_xStreamBufferGenericCreate(xBufferSizeBytes, xTriggerLevelBytes, xIsMessageBuffer, pxSendCompletedCallback, pxReceiveCompletedCallback) ((void)0)
#undef traceENTER_xStreamBufferGenericCreateStatic
#define traceENTER_xStreamBufferGenericCreateStatic(xBufferSizeBytes, xTriggerLevelBytes, xIsMessageBuffer, pucStreamBufferStorageArea, pxStaticStreamBuffer, pxSendCompletedCallback, pxReceiveCompletedCallback) ((void)0)
#undef traceENTER_vStreamBufferDelete
#define traceENTER_vStreamBufferDelete(xStreamBuffer) ((void)0)
#undef traceENTER_xStreamBufferReset
#define traceENTER_xStreamBufferReset(xStreamBuffer) ((void)0)
#undef traceENTER_xStreamBufferSetTriggerLevel
#define traceENTER_xStreamBufferSetTriggerLevel(xStreamBuffer, xTriggerLevel) ((void)0)
#undef traceENTER_xStreamBufferSpacesAvailable
#define traceENTER_xStreamBufferSpacesAvailable(xStreamBuffer) ((void)0)
#undef traceENTER_xStreamBufferBytesAvailable
#define traceENTER_xStreamBufferBytesAvailable(xStreamBuffer) ((void)0)
#undef traceENTER_xStreamBufferSend
#define traceENTER_xStreamBufferSend(xStreamBuffer, pvTxData, xDataLengthBytes, xTicksToWait) ((void)0)
#undef traceENTER_xStreamBufferSendFromISR
#define traceENTER_xStreamBufferSendFromISR(xStreamBuffer, pvTxData, xDataLengthBytes, pxHigherPriorityTaskWoken) ((void)0)
#undef traceENTER_xStreamBufferReceive
#define traceENTER_xStreamBufferReceive(xStreamBuffer, pvRxData, xBufferLengthBytes, xTicksToWait) ((void)0)
#undef traceENTER_xStreamBufferNextMessageLengthBytes
#define traceENTER_xStreamBufferNextMessageLengthBytes(xStreamBuffer) ((void)0)
#undef traceENTER_xStreamBufferReceiveFromISR
#define traceENTER_xStreamBufferReceiveFromISR(xStreamBuffer, pvRxData, xBufferLengthBytes, pxHigherPriorityTaskWoken) ((void)0)
#undef traceENTER_xStreamBufferIsEmpty
#define traceENTER_xStreamBufferIsEmpty(xStreamBuffer) ((void)0)
#undef traceENTER_xStreamBufferIsFull
#define traceENTER_xStreamBufferIsFull(xStreamBuffer) ((void)0)
#undef traceENTER_xStreamBufferSendCompletedFromISR
#define traceENTER_xStreamBufferSendCompletedFromISR(xStreamBuffer,pxHigherPriorityTaskWoken) ((void)0)
#undef traceENTER_xStreamBufferReceiveCompletedFromISR
#define traceENTER_xStreamBufferReceiveCompletedFromISR(xStreamBuffer, pxHigherPriorityTaskWoken) ((void)0)
#undef traceENTER_uxStreamBufferGetStreamBufferNumber
#define traceENTER_uxStreamBufferGetStreamBufferNumber(xStreamBuffer) ((void)0)
#undef traceENTER_vStreamBufferSetStreamBufferNumber
#define traceENTER_vStreamBufferSetStreamBufferNumber(xStreamBuffer, uxStreamBufferNumber) ((void)0)
#undef traceENTER_ucStreamBufferGetStreamBufferType
#define traceENTER_ucStreamBufferGetStreamBufferType(xStreamBuffer) ((void)0)
#undef traceRETURN_xQueueGenericReset
#define traceRETURN_xQueueGenericReset(xReturn) ((void)0)
#undef traceRETURN_xQueueGenericCreateStatic
#define traceRETURN_xQueueGenericCreateStatic(pxNewQueue) ((void)0)
#undef traceRETURN_xQueueGenericCreate
#define traceRETURN_xQueueGenericCreate(pxNewQueue) ((void)0)
#undef traceRETURN_xQueueCreateMutex
#define traceRETURN_xQueueCreateMutex(xNewQueue) ((void)0)
#undef traceRETURN_xQueueCreateMutexStatic
#define traceRETURN_xQueueCreateMutexStatic(xNewQueue) ((void)0)
#undef traceRETURN_xQueueGetMutexHolder
#define traceRETURN_xQueueGetMutexHolder(pxReturn) ((void)0)
#undef traceRETURN_xQueueGetMutexHolderFromISR
#define traceRETURN_xQueueGetMutexHolderFromISR(pxReturn) ((void)0)
#undef traceRETURN_xQueueGiveMutexRecursive
#define traceRETURN_xQueueGiveMutexRecursive(xReturn) ((void)0)
#undef traceRETURN_xQueueTakeMutexRecursive
#define traceRETURN_xQueueTakeMutexRecursive(xReturn) ((void)0)
#undef traceRETURN_xQueueCreateCountingSemaphoreStatic
#define traceRETURN_xQueueCreateCountingSemaphoreStatic(xHandle) ((void)0)
#undef traceRETURN_xQueueCreateCountingSemaphore
#define traceRETURN_xQueueCreateCountingSemaphore(xHandle) ((void)0)
#undef traceRETURN_xQueueGenericSend
#define traceRETURN_xQueueGenericSend(xReturn) ((void)0)
#undef traceRETURN_xQueueGenericSendFromISR
#define traceRETURN_xQueueGenericSendFromISR(xReturn) ((void)0)
#undef traceRETURN_xQueueGiveFromISR
#define traceRETURN_xQueueGiveFromISR(xReturn) ((void)0)
#undef traceRETURN_xQueueReceive
#define traceRETURN_xQueueReceive(xReturn) ((void)0)
#undef traceRETURN_xQueueSemaphoreTake
#define traceRETURN_xQueueSemaphoreTake(xReturn) ((void)0)
#undef traceRETURN_xQueuePeek
#define traceRETURN_xQueuePeek(xReturn) ((void)0)
#undef traceRETURN_xQueueReceiveFromISR
#define traceRETURN_xQueueReceiveFromISR(xReturn) ((void)0)
#undef traceRETURN_xQueuePeekFromISR
#define traceRETURN_xQueuePeekFromISR(xReturn) ((void)0)
#undef traceRETURN_uxQueueMessagesWaiting
#define traceRETURN_uxQueueMessagesWaiting(uxReturn) ((void)0)
#undef traceRETURN_uxQueueSpacesAvailable
#define traceRETURN_uxQueueSpacesAvailable(uxReturn) ((void)0)
#undef traceRETURN_uxQueueMessagesWaitingFromISR
#define traceRETURN_uxQueueMessagesWaitingFromISR(uxReturn) ((void)0)
#undef traceRETURN_vQueueDelete
#define traceRETURN_vQueueDelete() ((void)0)
#undef traceRETURN_uxQueueGetQueueNumber
#define traceRETURN_uxQueueGetQueueNumber(uxQueueNumber) ((void)0)
#undef traceRETURN_vQueueSetQueueNumber
#define traceRETURN_vQueueSetQueueNumber() ((void)0)
#undef traceRETURN_ucQueueGetQueueType
#define traceRETURN_ucQueueGetQueueType(ucQueueType) ((void)0)
#undef traceRETURN_xQueueIsQueueEmptyFromISR
#define traceRETURN_xQueueIsQueueEmptyFromISR(xReturn) ((void)0)
#undef traceRETURN_xQueueIsQueueFullFromISR
#define traceRETURN_xQueueIsQueueFullFromISR(xReturn) ((void)0)
#undef traceRETURN_xQueueCRSend
#define traceRETURN_xQueueCRSend(xReturn) ((void)0)
#undef traceRETURN_xQueueCRReceive
#define traceRETURN_xQueueCRReceive(xReturn) ((void)0)
#undef traceRETURN_xQueueCRSendFromISR
#define traceRETURN_xQueueCRSendFromISR(xCoRoutinePreviouslyWoken) ((void)0)
#undef traceRETURN_xQueueCRReceiveFromISR
#define traceRETURN_xQueueCRReceiveFromISR(xReturn) ((void)0)
#undef traceRETURN_vQueueAddToRegistry
#define traceRETURN_vQueueAddToRegistry() ((void)0)
#undef traceRETURN_pcQueueGetName
#define traceRETURN_pcQueueGetName(pcReturn) ((void)0)
#undef traceRETURN_vQueueUnregisterQueue
#define traceRETURN_vQueueUnregisterQueue() ((void)0)
#undef traceRETURN_vQueueWaitForMessageRestricted
#define traceRETURN_vQueueWaitForMessageRestricted() ((void)0)
#undef traceRETURN_xQueueCreateSet
#define traceRETURN_xQueueCreateSet(pxQueue) ((void)0)
#undef traceRETURN_xQueueAddToSet
#define traceRETURN_xQueueAddToSet(xReturn) ((void)0)
#undef traceRETURN_xQueueRemoveFromSet
#define traceRETURN_xQueueRemoveFromSet(xReturn) ((void)0)
#undef traceRETURN_xQueueSelectFromSet
#define traceRETURN_xQueueSelectFromSet(xReturn) ((void)0)
#undef traceRETURN_xQueueSelectFromSetFromISR
#define traceRETURN_xQueueSelectFromSetFromISR(xReturn) ((void)0)
#undef traceRETURN_xTaskCreateStatic
#define traceRETURN_xTaskCreateStatic(xReturn) ((void)0)
#undef traceRETURN_xTaskCreateRestrictedStatic
#define traceRETURN_xTaskCreateRestrictedStatic(xReturn) ((void)0)
#undef traceRETURN_xTaskCreateRestricted
#define traceRETURN_xTaskCreateRestricted(xReturn) ((void)0)
#undef traceRETURN_xTaskCreate
#define traceRETURN_xTaskCreate(xReturn) ((void)0)
#undef traceRETURN_vTaskDelete
#define traceRETURN_vTaskDelete() ((void)0)
#undef traceRETURN_xTaskDelayUntil
#define traceRETURN_xTaskDelayUntil(xShouldDelay) ((void)0)
#undef traceRETURN_vTaskDelay
#define traceRETURN_vTaskDelay() ((void)0)
#undef traceRETURN_eTaskGetState
#define traceRETURN_eTaskGetState(eReturn) ((void)0)
#undef traceRETURN_uxTaskPriorityGet
#define traceRETURN_uxTaskPriorityGet(uxReturn) ((void)0)
#undef traceRETURN_uxTaskPriorityGetFromISR
#define traceRETURN_uxTaskPriorityGetFromISR(uxReturn) ((void)0)
#undef traceRETURN_vTaskPrioritySet
#define traceRETURN_vTaskPrioritySet() ((void)0)
#undef traceRETURN_vTaskSuspend
#define traceRETURN_vTaskSuspend() ((void)0)
#undef traceRETURN_vTaskResume
#define traceRETURN_vTaskResume() ((void)0)
#undef traceRETURN_xTaskResumeFromISR
#define traceRETURN_xTaskResumeFromISR(xYieldRequired) ((void)0)
#undef traceRETURN_vTaskStartScheduler
#define traceRETURN_vTaskStartScheduler() ((void)0)
#undef traceRETURN_vTaskEndScheduler
#define traceRETURN_vTaskEndScheduler() ((void)0)
#undef traceRETURN_vTaskSuspendAll
#define traceRETURN_vTaskSuspendAll() ((void)0)
#undef traceRETURN_xTaskResumeAll
#define traceRETURN_xTaskResumeAll(xAlreadyYielded) ((void)0)
#undef traceRETURN_xTaskGetTickCount
#define traceRETURN_xTaskGetTickCount(xTicks) ((void)0)
#undef traceRETURN_xTaskGetTickCountFromISR
#define traceRETURN_xTaskGetTickCountFromISR(xReturn) ((void)0)
#undef traceRETURN_uxTaskGetNumberOfTasks
#define traceRETURN_uxTaskGetNumberOfTasks(uxCurrentNumberOfTasks) ((void)0)
#undef traceRETURN_pcTaskGetName
#define traceRETURN_pcTaskGetName(pcTaskName) ((void)0)
#undef traceRETURN_xTaskGetHandle
#define traceRETURN_xTaskGetHandle(pxTCB) ((void)0)
#undef traceRETURN_uxTaskGetSystemState
#define traceRETURN_uxTaskGetSystemState(uxTask) ((void)0)
#undef traceRETURN_xTaskGetIdleTaskHandle
#define traceRETURN_xTaskGetIdleTaskHandle(xIdleTaskHandle) ((void)0)
#undef traceRETURN_vTaskStepTick
#define traceRETURN_vTaskStepTick() ((void)0)
#undef traceRETURN_xTaskCatchUpTicks
#define traceRETURN_xTaskCatchUpTicks(xYieldOccurred) ((void)0)
#undef traceRETURN_xTaskAbortDelay
#define traceRETURN_xTaskAbortDelay(xReturn) ((void)0)
#undef traceRETURN_xTaskIncrementTick
#define traceRETURN_xTaskIncrementTick(xSwitchRequired) ((void)0)
#undef traceRETURN_vTaskSetApplicationTaskTag
#define traceRETURN_vTaskSetApplicationTaskTag() ((void)0)
#undef traceRETURN_xTaskGetApplicationTaskTag
#define traceRETURN_xTaskGetApplicationTaskTag(xReturn) ((void)0)
#undef traceRETURN_xTaskGetApplicationTaskTagFromISR
#define traceRETURN_xTaskGetApplicationTaskTagFromISR(xReturn) ((void)0)
#undef traceRETURN_xTaskCallApplicationTaskHook
#define traceRETURN_xTaskCallApplicationTaskHook(xReturn) ((void)0)
#undef traceRETURN_vTaskPlaceOnEventList
#define traceRETURN_vTaskPlaceOnEventList() ((void)0)
#undef traceRETURN_vTaskPlaceOnUnorderedEventList
#define traceRETURN_vTaskPlaceOnUnorderedEventList() ((void)0)
#undef traceRETURN_vTaskPlaceOnEventListRestricted
#define traceRETURN_vTaskPlaceOnEventListRestricted() ((void)0)
#undef traceRETURN_xTaskRemoveFromEventList
#define traceRETURN_xTaskRemoveFromEventList(xReturn) ((void)0)
#undef traceRETURN_vTaskRemoveFromUnorderedEventList
#define traceRETURN_vTaskRemoveFromUnorderedEventList() ((void)0)
#undef traceRETURN_vTaskSetTimeOutState
#define traceRETURN_vTaskSetTimeOutState() ((void)0)
#undef traceRETURN_vTaskInternalSetTimeOutState
#define traceRETURN_vTaskInternalSetTimeOutState() ((void)0)
#undef traceRETURN_xTaskCheckForTimeOut
#define traceRETURN_xTaskCheckForTimeOut(xReturn) ((void)0)
#undef traceRETURN_vTaskMissedYield
#define traceRETURN_vTaskMissedYield() ((void)0)
#undef traceRETURN_uxTaskGetTaskNumber
#define traceRETURN_uxTaskGetTaskNumber(uxReturn) ((void)0)
#undef traceRETURN_vTaskSetTaskNumber
#define traceRETURN_vTaskSetTaskNumber() ((void)0)
#undef traceRETURN_eTaskConfirmSleepModeStatus
#define traceRETURN_eTaskConfirmSleepModeStatus(eReturn) ((void)0)
#undef traceRETURN_vTaskSetThreadLocalStoragePointer
#define traceRETURN_vTaskSetThreadLocalStoragePointer() ((void)0)
#undef traceRETURN_pvTaskGetThreadLocalStoragePointer
#define traceRETURN_pvTaskGetThreadLocalStoragePointer(pvReturn) ((void)0)
#undef traceRETURN_vTaskAllocateMPURegions
#define traceRETURN_vTaskAllocateMPURegions() ((void)0)
#undef traceRETURN_vTaskGetInfo
#define traceRETURN_vTaskGetInfo() ((void)0)
#undef traceRETURN_uxTaskGetStackHighWaterMark2
#define traceRETURN_uxTaskGetStackHighWaterMark2(uxReturn) ((void)0)
#undef traceRETURN_uxTaskGetStackHighWaterMark
#define traceRETURN_uxTaskGetStackHighWaterMark(uxReturn) ((void)0)
#undef traceRETURN_pxTaskGetStackStart
#define traceRETURN_pxTaskGetStackStart(pxStack) ((void)0)
#undef traceRETURN_xTaskGetCurrentTaskHandle
#define traceRETURN_xTaskGetCurrentTaskHandle(xReturn) ((void)0)
#undef traceRETURN_xTaskGetSchedulerState
#define traceRETURN_xTaskGetSchedulerState(xReturn) ((void)0)
#undef traceRETURN_xTaskPriorityInherit
#define traceRETURN_xTaskPriorityInherit(xReturn) ((void)0)
#undef traceRETURN_xTaskPriorityDisinherit
#define traceRETURN_xTaskPriorityDisinherit(xReturn) ((void)0)
#undef traceRETURN_vTaskPriorityDisinheritAfterTimeout
#define traceRETURN_vTaskPriorityDisinheritAfterTimeout() ((void)0)
#undef traceRETURN_vTaskEnterCritical
#define traceRETURN_vTaskEnterCritical() ((void)0)
#undef traceRETURN_vTaskExitCritical
#define traceRETURN_vTaskExitCritical() ((void)0)
#undef traceRETURN_vTaskList
#define traceRETURN_vTaskList() ((void)0)
#undef traceRETURN_vTaskGetRunTimeStats
#define traceRETURN_vTaskGetRunTimeStats() ((void)0)
#undef traceRETURN_uxTaskResetEventItemValue
#define traceRETURN_uxTaskResetEventItemValue(uxReturn) ((void)0)
#undef traceRETURN_pvTaskIncrementMutexHeldCount
#define traceRETURN_pvTaskIncrementMutexHeldCount(pxCurrentTCB) ((void)0)
#undef traceRETURN_ulTaskGenericNotifyTake
#define traceRETURN_ulTaskGenericNotifyTake(ulReturn) ((void)0)
#undef traceRETURN_xTaskGenericNotifyWait
#define traceRETURN_xTaskGenericNotifyWait(xReturn) ((void)0)
#undef traceRETURN_xTaskGenericNotify
#define traceRETURN_xTaskGenericNotify(xReturn) ((void)0)
#undef traceRETURN_xTaskGenericNotifyFromISR
#define traceRETURN_xTaskGenericNotifyFromISR(xReturn) ((void)0)
#undef traceRETURN_vTaskGenericNotifyGiveFromISR
#define traceRETURN_vTaskGenericNotifyGiveFromISR() ((void)0)
#undef traceRETURN_xTaskGenericNotifyStateClear
#define traceRETURN_xTaskGenericNotifyStateClear(xReturn) ((void)0)
#undef traceRETURN_ulTaskGenericNotifyValueClear
#define traceRETURN_ulTaskGenericNotifyValueClear(ulReturn) ((void)0)
#undef traceRETURN_ulTaskGetIdleRunTimeCounter
#define traceRETURN_ulTaskGetIdleRunTimeCounter(ulReturn) ((void)0)
#undef traceRETURN_ulTaskGetIdleRunTimePercent
#define traceRETURN_ulTaskGetIdleRunTimePercent(ulReturn) ((void)0)
#undef traceRETURN_vTaskCoreAffinitySet
#define traceRETURN_vTaskCoreAffinitySet() ((void)0)
#undef traceRETURN_vTaskCoreAffinityGet
#define traceRETURN_vTaskCoreAffinityGet(uxCoreAffinityMask) ((void)0)
#undef traceRETURN_vTaskPreemptionDisable
#define traceRETURN_vTaskPreemptionDisable() ((void)0)
#undef traceRETURN_vTaskPreemptionEnable
#define traceRETURN_vTaskPreemptionEnable() ((void)0)
#undef traceRETURN_vTaskYieldWithinAPI
#define traceRETURN_vTaskYieldWithinAPI() ((void)0)
#undef traceRETURN_vTaskEnterCriticalFromISR
#define traceRETURN_vTaskEnterCriticalFromISR(uxSavedInterruptStatus) ((void)0)
#undef traceRETURN_vTaskExitCriticalFromISR
#define traceRETURN_vTaskExitCriticalFromISR() ((void)0)
#undef traceRETURN_ulTaskGetRunTimeCounter
#define traceRETURN_ulTaskGetRunTimeCounter(ulRunTimeCounter) ((void)0)
#undef traceRETURN_xTimerCreateTimerTask
#define traceRETURN_xTimerCreateTimerTask(xReturn) ((void)0)
#undef traceRETURN_xTimerCreate
#define traceRETURN_xTimerCreate(pxNewTimer) ((void)0)
#undef traceRETURN_xTimerCreateStatic
#define traceRETURN_xTimerCreateStatic(pxNewTimer) ((void)0)
#undef traceRETURN_xTimerGenericCommand
#define traceRETURN_xTimerGenericCommand(xReturn) ((void)0)
#undef traceRETURN_xTimerGenericCommandFromTask
#define traceRETURN_xTimerGenericCommandFromTask(xReturn) ((void)0)
#undef traceRETURN_xTimerGenericCommandFromISR
#define traceRETURN_xTimerGenericCommandFromISR(xReturn) ((void)0)
#undef traceRETURN_xTimerGetTimerDaemonTaskHandle
#define traceRETURN_xTimerGetTimerDaemonTaskHandle(xTimerTaskHandle) ((void)0)
#undef traceRETURN_xTimerGetPeriod
#define traceRETURN_xTimerGetPeriod(xTimerPeriodInTicks) ((void)0)
#undef traceRETURN_vTimerSetReloadMode
#define traceRETURN_vTimerSetReloadMode() ((void)0)
#undef traceRETURN_xTimerGetReloadMode
#define traceRETURN_xTimerGetReloadMode(xReturn) ((void)0)
#undef traceRETURN_xTimerGetExpiryTime
#define traceRETURN_xTimerGetExpiryTime(xReturn) ((void)0)
#undef traceRETURN_pcTimerGetName
#define traceRETURN_pcTimerGetName(pcTimerName) ((void)0)
#undef traceRETURN_xTimerIsTimerActive
#define traceRETURN_xTimerIsTimerActive(xReturn) ((void)0)
#undef traceRETURN_pvTimerGetTimerID
#define traceRETURN_pvTimerGetTimerID(pvReturn) ((void)0)
#undef traceRETURN_vTimerSetTimerID
#define traceRETURN_vTimerSetTimerID() ((void)0)
#undef traceRETURN_xTimerPendFunctionCallFromISR
#define traceRETURN_xTimerPendFunctionCallFromISR(xReturn) ((void)0)
#undef traceRETURN_xTimerPendFunctionCall
#define traceRETURN_xTimerPendFunctionCall(xReturn) ((void)0)
#undef traceRETURN_uxTimerGetTimerNumber
#define traceRETURN_uxTimerGetTimerNumber(uxTimerNumber) ((void)0)
#undef traceRETURN_vTimerSetTimerNumber
#define traceRETURN_vTimerSetTimerNumber() ((void)0)
#undef traceRETURN_vListInitialise
#define traceRETURN_vListInitialise() ((void)0)
#undef traceRETURN_vListInitialiseItem
#define traceRETURN_vListInitialiseItem() ((void)0)
#undef traceRETURN_vListInsertEnd
#define traceRETURN_vListInsertEnd() ((void)0)
#undef traceRETURN_vListInsert
#define traceRETURN_vListInsert() ((void)0)
#undef traceRETURN_uxListRemove
#define traceRETURN_uxListRemove(uxNumberOfItems) ((void)0)
#undef traceRETURN_xCoRoutineCreate
#define traceRETURN_xCoRoutineCreate(xReturn) ((void)0)
#undef traceRETURN_vCoRoutineAddToDelayedList
#define traceRETURN_vCoRoutineAddToDelayedList() ((void)0)
#undef traceRETURN_vCoRoutineSchedule
#define traceRETURN_vCoRoutineSchedule() ((void)0)
#undef traceRETURN_xCoRoutineRemoveFromEventList
#define traceRETURN_xCoRoutineRemoveFromEventList(xReturn) ((void)0)
#undef traceRETURN_xEventGroupCreateStatic
#define traceRETURN_xEventGroupCreateStatic(pxEventBits) ((void)0)
#undef traceRETURN_xEventGroupCreate
#define traceRETURN_xEventGroupCreate(pxEventBits) ((void)0)
#undef traceRETURN_xEventGroupSync
#define traceRETURN_xEventGroupSync(uxReturn) ((void)0)
#undef traceRETURN_xEventGroupWaitBits
#define traceRETURN_xEventGroupWaitBits(uxReturn) ((void)0)
#undef traceRETURN_xEventGroupClearBits
#define traceRETURN_xEventGroupClearBits(uxReturn) ((void)0)
#undef traceRETURN_xEventGroupClearBitsFromISR
#define traceRETURN_xEventGroupClearBitsFromISR(xReturn) ((void)0)
#undef traceRETURN_xEventGroupGetBitsFromISR
#define traceRETURN_xEventGroupGetBitsFromISR(uxReturn) ((void)0)
#undef traceRETURN_xEventGroupSetBits
#define traceRETURN_xEventGroupSetBits(uxEventBits) ((void)0)
#undef traceRETURN_vEventGroupDelete
#define traceRETURN_vEventGroupDelete() ((void)0)
#undef traceRETURN_vEventGroupSetBitsCallback
#define traceRETURN_vEventGroupSetBitsCallback() ((void)0)
#undef traceRETURN_vEventGroupClearBitsCallback
#define traceRETURN_vEventGroupClearBitsCallback() ((void)0)
#undef traceRETURN_xEventGroupSetBitsFromISR
#define traceRETURN_xEventGroupSetBitsFromISR(xReturn) ((void)0)
#undef traceRETURN_uxEventGroupGetNumber
#define traceRETURN_uxEventGroupGetNumber(xReturn) ((void)0)
#undef traceRETURN_vEventGroupSetNumber
#define traceRETURN_vEventGroupSetNumber() ((void)0)
#undef traceRETURN_xStreamBufferGenericCreate
#define traceRETURN_xStreamBufferGenericCreate(pucAllocatedMemory) ((void)0)
#undef traceRETURN_xStreamBufferGenericCreateStatic
#define traceRETURN_xStreamBufferGenericCreateStatic(xReturn) ((void)0)
#undef traceRETURN_vStreamBufferDelete
#define traceRETURN_vStreamBufferDelete() ((void)0)
#undef traceRETURN_xStreamBufferReset
#define traceRETURN_xStreamBufferReset(xReturn) ((void)0)
#undef traceRETURN_xStreamBufferSetTriggerLevel
#define traceRETURN_xStreamBufferSetTriggerLevel(xReturn) ((void)0)
#undef traceRETURN_xStreamBufferSpacesAvailable
#define traceRETURN_xStreamBufferSpacesAvailable(xSpace) ((void)0)
#undef traceRETURN_xStreamBufferBytesAvailable
#define traceRETURN_xStreamBufferBytesAvailable(xReturn) ((void)0)
#undef traceRETURN_xStreamBufferSend
#define traceRETURN_xStreamBufferSend(xReturn) ((void)0)
#undef traceRETURN_xStreamBufferSendFromISR
#define traceRETURN_xStreamBufferSendFromISR(xReturn) ((void)0)
#undef traceRETURN_xStreamBufferReceive
#define traceRETURN_xStreamBufferReceive(xReceivedLength) ((void)0)
#undef traceRETURN_xStreamBufferNextMessageLengthBytes
#define traceRETURN_xStreamBufferNextMessageLengthBytes(xReturn) ((void)0)
#undef traceRETURN_xStreamBufferReceiveFromISR
#define traceRETURN_xStreamBufferReceiveFromISR(xReceivedLength) ((void)0)
#undef traceRETURN_xStreamBufferIsEmpty
#define traceRETURN_xStreamBufferIsEmpty(xReturn) ((void)0)
#undef traceRETURN_xStreamBufferIsFull
#define traceRETURN_xStreamBufferIsFull(xReturn) ((void)0)
#undef traceRETURN_xStreamBufferSendCompletedFromISR
#define traceRETURN_xStreamBufferSendCompletedFromISR(xReturn) ((void)0)
#undef traceRETURN_xStreamBufferReceiveCompletedFromISR
#define traceRETURN_xStreamBufferReceiveCompletedFromISR(xReturn) ((void)0)
#undef traceRETURN_uxStreamBufferGetStreamBufferNumber
#define traceRETURN_uxStreamBufferGetStreamBufferNumber(uxStreamBufferNumber) ((void)0)
#undef traceRETURN_vStreamBufferSetStreamBufferNumber
#define traceRETURN_vStreamBufferSetStreamBufferNumber() ((void)0)
#undef traceRETURN_ucStreamBufferGetStreamBufferType
#define traceRETURN_ucStreamBufferGetStreamBufferType(ucFlags) ((void)0)
