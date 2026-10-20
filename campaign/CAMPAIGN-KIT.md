# Pause: student job-offer awareness kit

Status: ready-to-run materials, not an executed campaign. All examples are fictional. Malay copy is a draft awaiting review by a fluent speaker. No university endorsement, partnership or participant count is claimed.

## Purpose and facilitation

Help students identify what a recruiter is actually asking them to do, explain uncertainty, and verify independently. The checker is an educational prompt, not a fraud verdict. Run the local app on the facilitator’s device; never ask students to paste personal offers into a shared screen. Use `data/offers.json` instead.

Before the session: test the local server, print `campaign/poster.html`, review the three examples below, and nominate an appropriate student support contact. Ask participants not to disclose names, account numbers, financial losses or private messages in the group. Participation and feedback should be voluntary.

### Twenty-minute session

| Time | Activity | Facilitator prompt |
|---|---|---|
| 0–3 min | Show offer-01: payment assistant | “What is the work: providing a service, or moving money through your account?” |
| 3–10 min | Compare offer-18 payroll setup and offer-19 cafe | “Which details are missing? Which ordinary hiring practices could the checker flag?” |
| 10–15 min | Analyse examples and inspect highlighted evidence | “Which exact phrase caused the result? Could it have another meaning?” |
| 15–20 min | Independent verification role-play and exit question | “How would you locate the employer’s contact without using a number in the offer?” |

The payment assistant example should produce “Pause and verify.” The payroll example is intentionally ambiguous: normal payroll can require an account number, while account access and moving third-party funds are different. The cafe example has a weak WhatsApp signal; messaging-app use alone does not prove fraud. Never call a person or organisation a scammer based on this tool.

## Copy for a campus notice (draft; not posted)

**English**

A part-time job should not need control of your bank account. Pause if someone asks you to receive and move money, share an OTP or password, hand over a bank card, or pay to unlock earnings. Verify the employer through an official channel you find independently. Use the PDRM Semak Mule portal for a manual check: https://semakmule.rmp.gov.my/. No record is not proof that an offer is safe.

**Bahasa Melayu — draf**

Kerja sambilan tidak sepatutnya memerlukan kawalan akaun bank anda. Berhenti jika diminta menerima dan memindahkan wang, berkongsi OTP atau kata laluan, menyerahkan kad bank, atau membayar untuk mengeluarkan pendapatan. Sahkan majikan melalui saluran rasmi yang anda cari sendiri. Gunakan portal PDRM Semak Mule untuk semakan manual: https://semakmule.rmp.gov.my/. Tiada rekod bukan bukti bahawa tawaran selamat.

## Suggested partnership request (draft; not sent)

Subject: Request to review a student job-offer awareness session

We have prepared a local educational tool with 50 fictional job offers and explanations in English and draft Malay. We would welcome a student affairs review of the language, student support signposting and voluntary workshop format. The tool cannot establish fraud or safety, and we would not collect real job offers or personal financial details during a session. Would your team consider reviewing the materials before any proposed pilot? Dates, organisers, data handling and university branding would be agreed separately.

Do not imply that this draft establishes a partnership. Obtain the institution’s approval before using its logo or contacting students on its behalf.

## Evaluation that does not invent outcomes

Use the same short prompt before and after: “A recruiter asks to receive customers’ money in your account and forward it elsewhere. Name one concern and one independent verification step.” Score two items (concern and verification) from 0–1 each. Ask for a random participant code only if pre/post matching is needed; collect no name or contact. Explain storage, access and deletion before collecting anything. Free-text comments may contain personal information and need review before sharing.

Blank CSV fields for local recording:

```csv
session_id,date,participant_code,pre_concern_0_or_1,pre_verify_0_or_1,post_concern_0_or_1,post_verify_0_or_1,clarity_1_to_5,optional_comment
```

Record attendance separately as an aggregate. Report denominators, missing responses and self-selection. “Offers checked” should be an explicitly consented aggregate, not logs of students’ text. Do not convert poster impressions into participants or claim reduced fraud losses without a study.

## Follow-up and sources

If someone has shared account access or sent money, encourage them to contact their bank through an official channel and preserve messages. Do not investigate their accounts during the workshop.

PDRM describes Semak Mule as a manual check for accounts and telephone numbers used in commercial-crime cases: https://www.rmp.gov.my/news-detail/2022/09/17/besmartstayalert-letsfightscammertogether-scam-alert-guna-semak-mule-sebelum-teruskan-transaksi (checked 19 October 2026). The app links to the official portal and never scrapes it.
