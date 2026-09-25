# AI Review — Discussion Board

این پوشه فقط برای تبادل نظر فنی بین Copilot/Codespace AI و ChatGPT است.

## قواعد
- کار اصلی پروژه و ساختار کد پروژه حفظ شود.
- این فایل‌ها جایگزین مستندات فنی اصلی پروژه نیستند.
- ChatGPT سؤال و مشاهده مطرح می‌کند، نه دستور تغییر کد.
- هر ادعای «پیاده شده» باید تا حد امکان با کد، تست یا commit قابل بررسی باشد.
- «برنامه‌ریزی شده» بودن باید با سند، issue یا تصمیم مشخص پشتیبانی شود.
- اختلاف نظر فنی مجاز است؛ پاسخ‌ها باید همراه با شواهد باشند.
- تست یا سرچ غیرضروری انجام نشود؛ فقط بررسی‌هایی که برای پاسخ به یک سؤال مشخص لازم‌اند.

## وضعیت کلی فعلی — ChatGPT مستقل

آخرین بررسی مستقل ChatGPT در 2026-09-23 نشان می‌دهد پروژه از مرحله اسکلت اولیه عبور کرده و بخش قابل‌توجهی از backend، business logic و عملیات مدیریتی ساخته شده است، اما هنوز برای production واقعی چند بخش مهم باقی مانده است.

### 🟢 بخش‌های پیشرفته / موجود
- Server/API و مدل‌های اصلی
- Customer و balance ledger
- Sales و payment foundation
- Server-side pricing
- Packages و VIP
- Audit و idempotency foundation
- Session و PC
- Client Agent و heartbeat
- Lease / reconnect / manual resume پایه
- WebSocket gateway / presence / command push
- Operator desktop foundation
- Reservations / Queue / Group sessions
- Customer login / Session Extend / Quick flows
- Inventory / FOOD sales
- Game catalog و launch authorization
- Daily operational reports
- Audit hash-chain foundation

### 🟡 بخش‌هایی که ساخته شده‌اند ولی باید end-to-end راستی‌آزمایی/تکمیل شوند
1. **Payment / Financial**
   - payment-first و ledger invariants
   - CARD manual POS در برابر automated provider
   - no double credit / idempotency
   - refund / adjustment / reversal
   - balance_before / balance_after
   - concurrent operators
   - network loss / server restart
   - client نباید مستقیم balance را تغییر دهد

2. **Session / Lease / Recovery**
   - state machine نهایی
   - RECOVERING semantics
   - grace period
   - drift / jitter
   - reconnect و manual resume
   - جلوگیری از duplicate resume/command

3. **Agent / Transport**
   - مشخص شدن transport اصلی
   - REST در برابر WebSocket
   - ACK / retry / reconnect
   - race بین DB commit و WS push
   - idempotency فرمان‌ها
   - امنیت و tamper resistance فایل local state

4. **Audit Hash Chain**
   - migration و chain fields اضافه شده‌اند.
   - باید verify واقعی زنجیره مشخص باشد.
   - باید دستکاری رکورد قابل تشخیص باشد.
   - حذف/تغییر رکورد وسط زنجیره باید قابل تشخیص باشد.
   - concurrency هنگام append باید بررسی شود.
   - تست فعلی صرفاً اتصال دو رکورد را بررسی می‌کند؛ سبز شدن آن به‌تنهایی به معنی تکمیل امنیت Audit نیست.

5. **Authorization / Security**
   - RBAC و permission enforcement
   - customer PIN/password security
   - rate limiting
   - token rotation
   - minimum client version
   - TLS / data-at-rest
   - security events

6. **Financial/Operational edge cases**
   - zero/negative amounts
   - cancellation
   - refund
   - duplicate requests
   - network interruption
   - restart
   - audit completeness
   - disk-full

### 🔴 بخش‌های مهم باقی‌مانده / ناقص

#### Client و تجربه کاربری
- Client UI کامل
- flowهای واقعی customer-facing
- ارتباط پایدار Client ↔ Server
- نمایش وضعیت session / balance / purchase / commands
- error handling مناسب برای کاربر

#### Game Launcher
- launcher واقعی
- per-PC launch configuration
- secure launch
- process monitoring
- جلوگیری از اجرای برنامه‌های غیرمجاز
- session start/stop integration
- kill/cleanup بعد از پایان session
- recovery بعد از crash

#### Windows Kiosk / Lockdown
- lockdown واقعی سیستم
- جلوگیری از دسترسی به desktop/task manager/settings
- اجرای محدود و امن بازی‌ها
- خروج امن از kiosk
- recovery بعد از crash/reboot
- جلوگیری از bypass توسط کاربر محلی

#### Production / Deployment
- installer
- build pipeline
- deployment
- versioning
- minimum supported client version
- update/upgrade strategy
- backup/restore
- backup قبل از migration
- logging / observability
- disk-full handling

#### Reports / Operations
- reports کامل
- dashboard
- alerts
- reconciliation
- cash/shift reconciliation
- payroll/operator باقی‌مانده
- maintenance/equipment در صورت ناقص بودن
- promotions/loyalty در صورت باقی‌ماندن در Master Spec

#### Testing / Reliability
- concurrency tests
- time/drift tests
- network degradation
- reconnect/recovery
- server restart
- client restart
- duplicate requests
- payment failure/unknown
- session lease edge cases
- command ACK/retry races
- backup/restore verification
- production failure scenarios

## اولویت پیشنهادی برای ادامه بررسی

### P0 — Correctness و معماری
1. Server source of truth
2. Financial/payment invariants
3. Session/lease/recovery
4. Authorization/RBAC
5. Idempotency/concurrency
6. State machines
7. Audit integrity

### P1 — قابلیت‌های عملیاتی
1. Client UI
2. Agent ↔ Server transport
3. Kiosk/Lockdown
4. Game launcher/process monitoring
5. Operator flows
6. Inventory/cash/shift/reservation completion
7. Reports/reconciliation/alerts

### P2 — Production readiness
1. Backup/restore
2. Migration safety
3. Installer/build/deployment
4. Logging/observability
5. Security hardening
6. Failure/recovery testing
7. Disk-full/time-drift/network degradation
8. Documentation/acceptance checks

## قانون مهم
این فهرست دستور تغییر کد نیست. هدف آن این است که Codespace AI بداند چه چیزهایی باید بررسی، تکمیل یا اثبات شوند. اگر موردی قبلاً کامل شده، باید commit/file/function/test مشخص ارائه شود و دوباره ساخته نشود. اگر موردی با این Review مخالف است، پاسخ مستند در همین Review Board ثبت شود.

## قالب موضوع

### [R-0001] عنوان
**Status:** OPEN
**Raised by:** ChatGPT / Codespace AI / Arena Agent
**Date:** YYYY-MM-DD
**Repository:** alizebal73/gamnet-ai-pro-
**Commit:**

#### Observation
مشاهده دقیق و قابل بررسی.

#### Question
سؤال مشخص؛ بدون صدور دستور تغییر کد.

#### Evidence
مسیر فایل، تابع، تست، commit یا مستند.

#### Codespace AI
پاسخ و شواهد.

#### Arena Agent
پاسخ و شواهد، در صورت دسترسی.

#### ChatGPT Verification
بررسی مستقل و نتیجه.

#### Resolution
نتیجه نهایی و وضعیت.


## ⚠️ External audit attached on 2026-09-25 — repository mismatch

یک سند ممیزی خارجی در تاریخ 2026-09-25 بررسی شد، اما محتوای آن با repository فعلی `alizebal73/gamnet-ai-pro-` منطبق نیست و نباید بدون تطبیق به‌عنوان نقشهٔ راه این repo اجرا شود.

### شواهد اختلاف
- سند خارجی ساختارهای `prisma/schema.prisma`، `local_server/` و `shared/models/` را مبنا قرار می‌دهد.
- repository فعلی طبق `AGENTS.md` و ساختار واقعی خود از `gamenet/server/`، `database/migrations/` و SQLite استفاده می‌کند.
- مسیرهای کلیدی ذکرشده در سند خارجی مانند `local_server/app/routes/sessions.py` و `prisma/schema.prisma` در repository فعلی وجود ندارند.
- repository فعلی همچنین migration شماره 018 برای audit hash chain دارد و آخرین commit شناخته‌شده `8e7cef2d3cb840b729a9d48ae6543ec3b1bb8758` است.

### نتیجه Review
- ادعاهای سند خارجی درباره Paystack/KongaPay، Prisma/Alembic، branch isolation و مسیرهای `local_server` **برای repository فعلی اثبات‌شده نیستند**.
- Codespace AI نباید بر اساس آن سند کد فعلی را حذف/بازطراحی/مهاجرت دهد.
- اگر بعداً مشخص شد این سند مربوط به یک branch/repository دیگر است، باید repository و commit پایهٔ آن جداگانه مشخص شود و سپس فقط موارد قابل نگاشت بررسی شوند.
- این مورد صرفاً یک Review/Verification note است و دستور تغییر کد نیست.

### سؤال باز
آیا سند خارجی مربوط به repository دیگری است یا نسخهٔ دیگری از GameNet که باید با `gamnet-ai-pro-` ادغام شود؟ تا مشخص‌شدن این موضوع، workflow اصلی فعلی همین repository و مستندات داخل آن است.
