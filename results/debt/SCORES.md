Did the scan of the system as it was before each change point at what then broke? (14 changes)

| Level | Changes where Grace pointed at it beforehand |
|---|---|
| the deterministic detectors mention the header or a broken name | 0 of 14 |
| the model reports interface debt on the header | 5 of 14 |
| the model names the very symbol or member that broke | 2 of 14 |

Per change:

- **C01** cFE: Fix #1215, remove task registration calls (broke: CFE_ES_RegisterApp, CFE_ES_RegisterChildTask; 76 interface debts reported in cFE)
  - scan: nothing on it
  - model on the header: modules/core_api/fsw/inc/cfe_es.h:373 CFE_ES_RunLoop; modules/core_api/fsw/inc/cfe_es.h:347 CFE_ES_ExitApp; modules/core_api/fsw/inc/cfe_es.h:61 CFE_ES_TEST_LONG_MASK
- **C02** osal: fix #559 Refactoring UT_SetForceFail to UT_SetDefaultReturnValue (broke: UT_SetForceFail; 0 interface debts reported in osal)
  - scan: nothing on it
  - model on the header: nothing
- **C03** cFE: Fix #2473, document and use topicid numbers for cfe (broke: CFE_PLATFORM_CMD_MID_BASE, CFE_PLATFORM_TLM_MID_BASE; 66 interface debts reported in cFE)
  - scan: nothing on it
  - model on the header: nothing
- **C04** osal: Fix #853, remove OS_TaskRegister (broke: OS_TaskRegister; 0 interface debts reported in osal)
  - scan: nothing on it
  - model on the header: nothing
- **C05** osal: Fix #737, UT_Stub_CheckForceFail -> UT_Stub_CheckDefaultReturnValue (broke: UT_Stub_CheckForceFail; 0 interface debts reported in osal)
  - scan: nothing on it
  - model on the header: nothing
- **C06** PSP: Fix #280, remove psp configdata global object (broke: CFE_PSP_VERSION; 0 interface debts reported in PSP)
  - scan: nothing on it
  - model on the header: nothing
- **C07** osal: Fix #262, Deprecates OS_FS_* defines that aren't unique to FS (broke: OS_FS_ERROR, OS_FS_ERR_INVALID_POINTER, OS_FS_SUCCESS; 0 interface debts reported in osal)
  - scan: nothing on it
  - model on the header: nothing
- **C08** EdsLib: Fix #85, updates to struct/typedef names (broke: CFE_HDR_CommandHeader_Buffer_t, CFE_HDR_CommandHeader_PackedBuffer_t, CFE_HDR_CommandHeader_t, CFE_HDR_TelemetryHeader_PackedBuffer_t, CFE_SB_Telecommand_Interface_ID, CFE_SB_Telemetry_Interface_ID; 0 interface debts reported in EdsLib)
  - scan: nothing on it
  - model on the header: nothing
- **C09** cFE: Fix #2467, message integrity API (broke: CFE_MSG_UpdateHeader; 74 interface debts reported in cFE)
  - scan: nothing on it
  - model on the header: modules/core_api/fsw/inc/cfe_msg.h:61 CFE_MSG_Init; modules/core_api/fsw/inc/cfe_msg.h:708 CFE_SB_MsgId_t; modules/core_api/fsw/inc/cfe_msg.h:656 CFE_TIME_SysTime_t
- **C10** cFE: Fix #815, remove all deprecated code (broke: CFE_ES_APP_ERROR, CFE_ES_APP_RUN, CFE_ES_SHELL_TLM_MID, CFE_EVS_CRITICAL, CFE_EVS_DEBUG, CFE_EVS_ERROR, CFE_EVS_INFORMATION; 75 interface debts reported in cFE)
  - scan: nothing on it
  - model on the header: fsw/cfe-core/src/inc/cfe_es.h:114 CFE_ES_PROCESSOR_RESET; fsw/cfe-core/src/inc/cfe_es.h:344 CFE_ES_STATIC_POOL_TYPE; fsw/cfe-core/src/inc/cfe_es.h:63 CFE_ES_MAX_MEMPOOL_BLOCK_SIZES
- **F01** osal: Fix #429, update OS_time_t definition to 64-bit ticks (broke: OS_time_t, microsecs; 0 interface debts reported in osal)
  - scan: nothing on it
  - model on the header: nothing
- **F02** cFE: Fix #1009, Alignment pattern - core updates (broke: BaseMsg, CFE_SB_CmdHdr_t, CFE_SB_TlmHdr_t; 72 interface debts reported in cFE)
  - scan: nothing on it
  - model on the header: fsw/cfe-core/src/inc/cfe_sb.h:141 CFE_SB_CmdHdr_t.Cmd; fsw/cfe-core/src/inc/cfe_sb.h:147 CFE_SB_TlmHdr_t.Tlm; fsw/cfe-core/src/inc/cfe_sb.h:151 CFE_SB_CMD_HDR_SIZE
  - model on the name, line 141: `CFE_MSG_CommandHeader_t Cmd;` — The union exposes the command header and base message as directly accessible members, so user code can depend on the current header layout and type-punning. If cFE changes CFE_MSG_CommandHeader_t fields, order, alignment, or the base message representation, users that read or cast Cmd/BaseMsg must change.
  - model on the name, line 147: `CFE_MSG_TelemetryHeader_t Tlm;` — The union exposes the telemetry header and base message as directly accessible members, tying user code to the current telemetry header layout. If cFE changes the telemetry header fields, size, or base message representation, users that access Tlm/BaseMsg must change.
- **F03** cFE: Fix #2514, change CFE_MSG_Message from union to struct (broke: Byte, CFE_MSG_Message; 71 interface debts reported in cFE)
  - scan: nothing on it
  - model on the header: nothing
- **F04** cFE: Fix #711, Update SB/CCSDS FSW for msg module (broke: CCSDS_CommandPacket_t, CCSDS_TelemetryPacket_t, CFE_SB_Msg_t, SpacePacket; 78 interface debts reported in cFE)
  - scan: nothing on it
  - model on the header: fsw/cfe-core/src/inc/ccsds.h:164 CCSDS_SpacePacket_t.ApidQ; fsw/cfe-core/src/inc/ccsds.h:53 CCSDS_TIME_SIZE; fsw/cfe-core/src/inc/ccsds.h:88 CCSDS_PriHdr_t.StreamId
  - model on the name, line 211: `typedef CCSDS_CommandPacket_t CCSDS_CmdPkt_t;` — The deprecated CFE 6.5 alias keeps an old name alive in the public contract; users may continue to use CCSDS_CmdPkt_t, so any future removal or semantic change forces coordinated migration across dependent repositories.
  - model on the name, line 154: `uint8 Byte[sizeof(CCSDS_PriHdr_t)]; /**< \brief Allows byte-level access` — Users can index raw header bytes or rely on the primary header occupying exactly this array; any change to CCSDS_PriHdr_t size, field order, padding, or endianness silently breaks every app that parses or patches messages.
