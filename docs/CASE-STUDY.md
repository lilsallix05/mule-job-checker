# Pause: explaining risky requests in student job offers

## Problem

Students are sometimes offered "part-time work" that really means routing other people's money through their own bank account. A useful tool has to expose the requested action without accusing an employer or declaring an offer safe. It also has to handle ordinary hiring details, such as a WhatsApp contact or a payroll account number, without treating them as proof of fraud.

## Implementation

Pause is a local Python application with a responsive browser interface. Twenty weighted rules, written for English and draft Malay wording, return exact evidence offsets and an explanation for each match. A simple negation heuristic handles some safety notices ("we never ask for your OTP"). Contrast words such as "but" reset that heuristic, so "we never ask for passwords, but share your OTP" still flags the OTP request. Each rule counts once, so repeating a phrase cannot inflate the score.

The interface supports pasted text, TXT/CSV/JSON imports (single or batch), a fictional example library, highlighted excerpts, JSON export, printing and clearing the session. It has no database and makes no automatic external calls.

A supervised multinomial Naive Bayes model is trained on the included corpus and shown separately from the rules. It abstains when the input contains no words it knows.

## What was measured

The corpus has 50 authored synthetic offers: 25 scenarios, each in English and Malay. The rules match all 50 intended priorities. The same examples shaped the rules, so this is a consistency check, not an accuracy estimate.

The model trains on 34 offers and is tested on 16 from different scenario families. Translations stay on the same side of the split and the vocabulary comes from training data only. It labels 8 of 16 held-out offers correctly. The "pause and verify" class has precision 6/11 and recall 6/6. The ambiguous "clarify the details" class has precision 0 and recall 0/6. That weakness is the reason the model stays labelled as experimental and cannot overrule the rules. The full predictions and matrix are in `evidence/model-evaluation.json`; nothing was tuned to hide these errors.

## Tradeoffs and limits

Rules are transparent but miss novel phrasing and can flag ordinary payroll requests. Regular expressions are not language understanding. The small synthetic model generalises poorly; more code would not turn its numbers into field evidence. The next step is a consented, independently labelled set of real offers and an evaluation designed before any tuning. The Malay wording needs review by a fluent speaker.

No live bot account, bank lookup, student pilot, campaign, institutional partnership or deployment exists.
