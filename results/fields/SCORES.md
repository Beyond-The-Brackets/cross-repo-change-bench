| Tool | Model | Users named (of 10) | Recall | Files named | Repositories named | Confirmed | Precision (lower bound) | Changes with a warning (of 4) |
|---|---|---|---|---|---|---|---|---|
| grace | none | 10 | 100 % | 15 of 17 (88 %) | 22 | 10 | 45 % | 4 |
| grace (breaks only) | none | 9 | 90 % | 14 of 17 (82 %) | 11 | 9 | 82 % | 3 |
| model-diff+list | alibaba/qwen3-coder-30b-a3b | 6 | 60 % | 0 of 17 (0 %) | 47 | 6 | 13 % | 4 |
| grace-main-before | none | 5 | 50 % | 5 of 17 (29 %) | 17 | 5 | 29 % | 2 |
| grace-main-before (breaks only) | none | 1 | 10 % | 0 of 17 (0 %) | 3 | 1 | 33 % | 1 |
| model-diff | alibaba/qwen3-coder-30b-a3b | 0 | 0 % | 0 of 17 (0 %) | 1 | 0 | 0 % | 4 |
| pr-agent | alibaba/qwen3-coder-30b-a3b | 0 | 0 % | 0 of 17 (0 %) | 0 | 0 | n/a | 1 |

Recall by kind of evidence:

| Tool | direct | later |
|---|---|---|
| grace | 8 of 8 | 2 of 2 |
| grace (breaks only) | 7 of 8 | 2 of 2 |
| model-diff+list | 5 of 8 | 1 of 2 |
| grace-main-before | 5 of 8 | 0 of 2 |
| grace-main-before (breaks only) | 1 of 8 | 0 of 2 |
| model-diff | 0 of 8 | 0 of 2 |
| pr-agent | 0 of 8 | 0 of 2 |

Per change (users named / missed):

- **F01** osal `7e34a2c224` Fix #429, update OS_time_t definition to 64-bit ticks
  - grace: named HS, PSP, SBN, cFE
  - grace (breaks only): named HS, PSP, SBN, cFE
  - model-diff+list: named HS, cFE; missed PSP, SBN; not confirmed CF, DS, FM, HK, LC, MD, SC, ci_lab, sample_app, sch_lab
  - grace-main-before: named none; missed HS, PSP, SBN, cFE
  - grace-main-before (breaks only): named none; missed HS, PSP, SBN, cFE
  - model-diff: named none; missed HS, PSP, SBN, cFE
  - pr-agent: named none; missed HS, PSP, SBN, cFE
- **F02** cFE `d127a160ca` Fix #1009, Alignment pattern - core updates
  - grace: named ci_lab, sample_app, sch_lab, to_lab; not confirmed CF, CS, DS, FM, HK, HS, LC, MD, SBN, SC
  - grace (breaks only): named ci_lab, sample_app, sch_lab, to_lab
  - model-diff+list: named ci_lab, sample_app, sch_lab; missed to_lab; not confirmed elf2cfetbl, osal, sample_lib, tblCRCTool
  - grace-main-before: named ci_lab, sample_app, sch_lab, to_lab; not confirmed CF, CS, DS, FM, HK, HS, LC, MD, SBN, SC
  - grace-main-before (breaks only): named none; missed ci_lab, sample_app, sch_lab, to_lab
  - model-diff: named none; missed ci_lab, sample_app, sch_lab, to_lab
  - pr-agent: named none; missed ci_lab, sample_app, sch_lab, to_lab
- **F03** cFE `777feec3ac` Fix #2514, change CFE_MSG_Message from union to struct
  - grace: named EdsLib
  - grace (breaks only): named none; missed EdsLib
  - model-diff+list: named none; missed EdsLib; not confirmed CF, CS, DS, FM, HK, LC, MD, SBN, SC, ci_lab, osal, sample_app, tblCRCTool, to_lab
  - grace-main-before: named none; missed EdsLib
  - grace-main-before (breaks only): named none; missed EdsLib
  - model-diff: named none; missed EdsLib
  - pr-agent: named none; missed EdsLib
- **F04** cFE `8563679518` Fix #711, Update SB/CCSDS FSW for msg module
  - grace: named SBN; not confirmed CF, EdsLib
  - grace (breaks only): named SBN; not confirmed CF, EdsLib
  - model-diff+list: named SBN; not confirmed CF, CS, DS, FM, HK, HS, LC, MD, ci_lab, sample_app, sample_lib, sch_lab, to_lab
  - grace-main-before: named SBN; not confirmed CF, EdsLib
  - grace-main-before (breaks only): named SBN; not confirmed CF, EdsLib
  - model-diff: named none; missed SBN; not confirmed osal
  - pr-agent: named none; missed SBN
