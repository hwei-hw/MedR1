# MedR1
The distilled medical language model from DeepSeek-R1(671B).

## Overview
This project aims to enhance medical reasoning capabilities in compact models through knowledge distillation from the DeepSeek-R1 (671B) model. By leveraging domain-specific medical data, we try to distill critical medical knowledge into a significantly smaller model while maintaining/improving diagnostic reasoning performance in healthcare contexts.

## Key outcomes:
- 90%+ size reduction compared to the original 671B parameter model
- Enhanced performance on medical QA, and clinical reasoning.
- Optimized for deployment in resource-constrained medical environments.

## Features
- **Curated Reasoning Datasets**: Fully Open distilled datasets with think process in the medical domain (~170K).
- **Clinical-Ready Architecture**: Flexible distilled model sizes (3B/7B/13B parameter variants).

## Experiments

**We will update&open more experimental results, datasets, weights and code as soon as possible!**

### 1. Will the official distilled version of the model perform better than the original model in medical Q&A? 

**Actually, Not!**

We evaluate the official distilled R1 model on the following datasets (accuracy):

| Model                | MedQA-US-TEST | MedMCQA-VALIDATION |
|-----------------------|-----------------|----------------|
| GPT-40-mini        | 70.78    | 65.85    |
| Qwen2.5-7B-Instruct | 50.59          | 55.24         |
| DeepSeek-R1-Distill-Qwen-7B      | 38.81     | 38.18 |
| DeepSeek-R1-Distill-Qwen-1.5B | 27.18 | 32.32 |

### 2. Can distillation improve the model's reasoning ability?

**Yes!**

We first distilled the 8K data, then fine-tuned the Qwen2.5-7B-Instruct using Lora, and then tested the following question:
```text
Question: A 37-year-old-woman presents to her primary care physician requesting a new form of birth control. She has been utilizing oral contraceptive pills (OCPs) for the past 8 years, but asks to switch to an intrauterine device (IUD). Her vital signs are: blood pressure 118/78 mm Hg, pulse 73/min and respiratory rate 16/min. She is afebrile. Physical examination is within normal limits. Which of the following past medical history statements would make copper IUD placement contraindicated in this patient?\n Please only select the correct option index (e.g. A) from following options:\nA: A history of stroke or venous thromboembolism\n B: Current tobacco use\n C: Active or recurrent pelvic inflammatory disease (PID)\n D: Past medical history of breast cancer\n E: Known liver neoplasm
Ground Truth: C
```

Qwen2.5-7B-Instruct (with default system prompt):
```text
A: A history of stroke or venous thromboembolism

Copper IUD placement is generally considered safe, but it is contraindicated in patients with a history of stroke or venous thromboembolism due to the increased risk of thrombotic events. Therefore, the correct answer is A.
```
Qwen2.5-7B-Instruct-Med-Distill(without system prompt):
```text
The correct answer is **C**.

Explanation: The copper IUD (intrauterine device) is generally considered safe for most women, but there are certain contraindications. Active or recurrent pelvic inflammatory disease (PID) is a significant risk factor because the presence of infection can lead to severe complications such as pelvic infection or sepsis. Therefore, placing a copper IUD in a patient with active or recurrent PID would be contraindicated. Other options like a history of stroke or venous thromboembolism (A), current tobacco use (B), a history of breast cancer (D), or a known liver neoplasm (E) do not necessarily contraindicate copper IUD placement unless they are associated with specific risks. For example, current tobacco use increases the risk of uterine perforation during insertion but doesn't absolutely contraindicate it; similarly, liver neoplasms might affect other contraceptive methods but aren't absolute contraindications for copper IUDs.
```
Qwen2.5-7B-Instruct-Med-Distill (with system prompt:
```system prompt: Your role as an assistant involves thoroughly exploring questions through a systematic long thinking process (<think>...</think>)\nbefore providing the final precise and accurate solutions (<answer>...</answer>). This requires engaging in a comprehensive cycle of\nanalysis, summarizing, exploration, reassessment, reflection, backtracing, and iteration to develop well-considered\nthinking process. ```)
```text
<think>Okay, let's tackle this question step by step. The patient is a 37-year-old woman who wants to switch from OCPs to an IUD. The question is asking which past medical history makes copper IUD placement contraindicated. The options are A through E.

First, I need to recall the indications and contraindications for IUD insertion, especially focusing on copper IUDs like the ParaGard. The main points here are the risks associated with different conditions that could affect the safety or efficacy of the IUD.

Starting with the options:

A: History of stroke or venous thromboembolism (VTE). I remember that VTE is a relative contraindication for hormonal contraceptives because they increase the risk of blood clots. However, copper IUDs don't contain hormones, so they shouldn't have the same clotting risk. So maybe this isn't the answer. But wait, some sources might say that any condition that increases the risk of VTE is a contraindication for any type of IUD? Let me think. The copper IUD's mechanism is physical rather than hormonal, so theoretically, it shouldn't contribute to clotting issues. But maybe there's a different angle. Alternatively, if she has a history of stroke or VTE, perhaps other factors are at play. But since the question is about copper IUD specifically, maybe A is not the answer here.

B: Current tobacco use. I know that smoking increases the risk of complications with hormonal contraceptives. However, copper IUDs don't rely on hormones, so current tobacco use might not be a contraindication. Unless there's another reason related to smoking. For example, if she smokes heavily, maybe there's a higher risk of expulsion or other issues, but I'm not sure. Maybe this is a distractor. Let's move on.

C: Active or recurrent pelvic inflammatory disease (PID). PID can lead to scarring and adhesions in the uterus, which could make the IUD placement more difficult or increase the risk of uterine perforation. Since the copper IUD relies on being in place without hormonal effects, active or recurrent PID might be a contraindication because of the potential for complications during insertion. If she has active PID, it's probably best to treat that first before considering an IUD. So this seems like a strong candidate.

D: Past medical history of breast cancer. I recall that hormonal contraceptives, including OCPs, are generally not recommended for women with a history of breast cancer due to increased risk of recurrence. However, copper IUDs are hormone-free, so their use might be acceptable. So D might not be the answer here.

E: Known liver neoplasm. Liver tumors can be problematic because the body processes hormones differently. Since copper IUDs don't involve hormones, liver issues might not be a direct contraindication. However, if the tumor is active or if there's concern about metastasis, perhaps. But again, I need to check. I think in general, non-hormonal methods like IUDs are okay unless there's a specific issue. So E might not be the answer.

So going back to the options. The key here is distinguishing between hormone-based and non-hormone based methods. The copper IUD doesn't rely on hormones, so most contraindications related to hormonal contraceptives (like stroke/VTE, breast cancer, liver issues) would not apply. The main concerns are related to pelvic infections, active cancers, or other anatomical issues.

Looking at the options again:

A: Stroke/VTE – Not a contraindication for copper IUD.

B: Smoking – Not a contraindication for copper IUD.

C: PID – This is a contraindication because of the risk of complications during insertion and the potential for scarring leading to expulsion or perforation.

D: Breast cancer – Hormonal contraceptives are contraindicated, but copper IUDs are okay.

E: Liver neoplasm – Not a direct contraindication unless the tumor is active or causing issues.

Therefore, the correct answer should be C.
From v4.47 onwards, when a model cache is to be returned, `generate` will return a `Cache` instance instead by default (as opposed to the legacy tuple of tuples format). If you want to keep returning the legacy format, please set `return_legacy_cache=True`.
</think>
<answer>C</answer>
```
