| Tool | Model | Users named (of 45) | Recall | Files named | Repositories named | Confirmed | Precision (lower bound) | Changes with a warning (of 10) |
|---|---|---|---|---|---|---|---|---|
| grace | none | 45 | 100 % | 131 of 138 (95 %) | 46 | 45 | 98 % | 10 |
| grace (breaks only) | none | 35 | 78 % | 96 of 138 (70 %) | 36 | 35 | 97 % | 7 |
| model-diff+list | alibaba/qwen3-coder-30b-a3b | 30 | 67 % | 0 of 138 (0 %) | 142 | 30 | 21 % | 10 |
| model-diff | alibaba/qwen3-coder-30b-a3b | 0 | 0 % | 0 of 138 (0 %) | 1 | 0 | 0 % | 10 |
| pr-agent | alibaba/qwen3-coder-30b-a3b | 0 | 0 % | 0 of 138 (0 %) | 0 | 0 | n/a | 5 |

Recall by kind of evidence:

| Tool | direct | later | release |
|---|---|---|---|
| grace | 21 of 21 | 18 of 18 | 6 of 6 |
| grace (breaks only) | 14 of 21 | 15 of 18 | 6 of 6 |
| model-diff+list | 17 of 21 | 7 of 18 | 6 of 6 |
| model-diff | 0 of 21 | 0 of 18 | 0 of 6 |
| pr-agent | 0 of 21 | 0 of 18 | 0 of 6 |

Per change (users named / missed):

- **C01** cFE `8c70e950b3` Fix #1215, remove task registration calls
  - grace: named CF, CS, DS, FM, HK, HS, LC, MD, SBN, SC, ci_lab, sample_app, sch_lab, to_lab
  - grace (breaks only): named CF, CS, DS, FM, HK, HS, LC, MD, SBN, SC, ci_lab, sample_app, sch_lab, to_lab
  - model-diff+list: named ci_lab, sample_app, sch_lab, to_lab; missed CF, CS, DS, FM, HK, HS, LC, MD, SBN, SC; not confirmed elf2cfetbl, sample_lib
  - model-diff: named none; missed CF, CS, DS, FM, HK, HS, LC, MD, SBN, SC, ci_lab, sample_app, sch_lab, to_lab
  - pr-agent: named none; missed CF, CS, DS, FM, HK, HS, LC, MD, SBN, SC, ci_lab, sample_app, sch_lab, to_lab
- **C02** osal `52ee87136d` fix #559 Refactoring UT_SetForceFail to UT_SetDefaultReturnValue
  - grace: named PSP, cFE, sample_app, sample_lib
  - grace (breaks only): named none; missed PSP, cFE, sample_app, sample_lib
  - model-diff+list: named PSP, cFE, sample_app, sample_lib; not confirmed CF, CS, DS, EdsLib, FM, HK, HS, LC, MD, SBN, SC, ci_lab, sch_lab, to_lab
  - model-diff: named none; missed PSP, cFE, sample_app, sample_lib
  - pr-agent: named none; missed PSP, cFE, sample_app, sample_lib
- **C03** cFE `f3cdfbe3ab` Fix #2473, document and use topicid numbers for cfe
  - grace: named DS, HK, LC, MD, SC
  - grace (breaks only): named DS, HK, LC, MD, SC
  - model-diff+list: named DS, HK; missed LC, MD, SC; not confirmed CS, FM, ci_lab, elf2cfetbl, osal, sample_app, sample_lib, sch_lab, tblCRCTool, to_lab
  - model-diff: named none; missed DS, HK, LC, MD, SC
  - pr-agent: named none; missed DS, HK, LC, MD, SC
- **C04** osal `367007601e` Fix #853, remove OS_TaskRegister
  - grace: named CF, cFE
  - grace (breaks only): named CF, cFE
  - model-diff+list: named CF, cFE; not confirmed CS, DS, EdsLib, FM, HK, HS, LC, MD, PSP, SBN, SC, ci_lab, elf2cfetbl, sample_app, tblCRCTool, to_lab
  - model-diff: named none; missed CF, cFE
  - pr-agent: named none; missed CF, cFE
- **C05** osal `b2447bdcbd` Fix #737, UT_Stub_CheckForceFail -> UT_Stub_CheckDefaultReturnValue
  - grace: named cFE
  - grace (breaks only): named cFE
  - model-diff+list: named cFE; not confirmed CF, CS, DS, EdsLib, FM, HK, HS, LC, MD, PSP, SBN, SC, ci_lab, elf2cfetbl, sample_app, sample_lib, sch_lab, tblCRCTool, to_lab
  - model-diff: named none; missed cFE
  - pr-agent: named none; missed cFE
- **C06** PSP `a6c07e1a80` Fix #280, remove psp configdata global object
  - grace: named cFE
  - grace (breaks only): named cFE
  - model-diff+list: named cFE; not confirmed CF, CS, DS, EdsLib, FM, HK, HS, LC, MD, SBN, SC, ci_lab, osal, sample_app
  - model-diff: named none; missed cFE
  - pr-agent: named none; missed cFE
- **C07** osal `41862fd771` Fix #262, Deprecates OS_FS_* defines that aren't unique to FS
  - grace: named CF, CS, FM, cFE
  - grace (breaks only): named none; missed CF, CS, FM, cFE
  - model-diff+list: named CF, CS, cFE; missed FM; not confirmed ci_lab, elf2cfetbl, sample_app, sch_lab, to_lab
  - model-diff: named none; missed CF, CS, FM, cFE
  - pr-agent: named none; missed CF, CS, FM, cFE
- **C08** EdsLib `147dc08653` Fix #85, updates to struct/typedef names
  - grace: named ci_lab, to_lab
  - grace (breaks only): named none; missed ci_lab, to_lab
  - model-diff+list: named ci_lab, to_lab; not confirmed elf2cfetbl, osal, sample_app, sample_lib, sch_lab, tblCRCTool
  - model-diff: named none; missed ci_lab, to_lab
  - pr-agent: named none; missed ci_lab, to_lab
- **C09** cFE `4a4ada462a` Fix #2467, message integrity API
  - grace: named EdsLib
  - grace (breaks only): named EdsLib
  - model-diff+list: named none; missed EdsLib; not confirmed CF, CS, DS, FM, HK, HS, LC, MD, SBN, SC, ci_lab, elf2cfetbl, osal, sample_app, sample_lib, sch_lab, tblCRCTool, to_lab
  - model-diff: named none; missed EdsLib; not confirmed SBN
  - pr-agent: named none; missed EdsLib
- **C10** cFE `37a5ac9c62` Fix #815, remove all deprecated code
  - grace: named CF, CS, DS, FM, HK, HS, LC, MD, SBN, SC, to_lab; not confirmed osal
  - grace (breaks only): named CF, CS, DS, FM, HK, HS, LC, MD, SBN, SC, to_lab; not confirmed osal
  - model-diff+list: named CF, CS, DS, FM, HK, HS, LC, MD, SBN, SC, to_lab; not confirmed EdsLib, ci_lab, elf2cfetbl, osal, sample_app, sample_lib, sch_lab, tblCRCTool
  - model-diff: named none; missed CF, CS, DS, FM, HK, HS, LC, MD, SBN, SC, to_lab
  - pr-agent: named none; missed CF, CS, DS, FM, HK, HS, LC, MD, SBN, SC, to_lab
