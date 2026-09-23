# MASTER REVIEW — GameNet Pro

> این فایل مرجع بررسی مستقل ChatGPT برای Codespace AI است. هدف آن نشان دادن وضعیت، نقص‌ها و اولویت‌های بررسی است؛ «دستور تغییر کد» نیست. کار اصلی پروژه باید ادامه پیدا کند و هر ادعای تکمیل با کد/commit/test قابل بررسی باشد.

## 1) وضعیت همکاری
- Repository: `alizebal73/gamnet-ai-pro-`
- Review board: `.ai-review/`
- Codespace AI باید این فایل را در شروع نوبت کاری بررسی کند و پاسخ/شواهد خود را در `DISCUSSION.md` یا فایل مناسب ثبت کند.
- ChatGPT از بیرون repository بررسی مستقل انجام می‌دهد.
- بررسی‌های غیرضروری، تست‌های تکراری و جست‌وجوی اضافی انجام نشود.

## 2) اصل معماری که باید در کل پروژه حفظ شود
- Server = source of truth.
- Client نباید مستقیم SQLite/DB را تغییر دهد.
- Customer ≠ Credit ≠ Session ≠ PC.
- Payment First → Activation Second.
- تمام عملیات مالی idempotent و audit-able باشند.
- حذف سخت اطلاعات مالی ممنوع؛ refund/adjustment/reversal استفاده شود.
- زمان‌ها UTC ISO و مبالغ integer minor units.
- رمز/PIN با hashing امن.
- پس از reconnect، resume خودکار ممنوع؛ manual resume.
- تغییر schema فقط با migration و بررسی سازگاری.
- تغییرات کوچک و قابل ردیابی، بدون شکستن معماری موجود.

## 3) نقشه وضعیت فعلی

### موجود / نسبتاً کامل
- پایه server/API و مدل‌های اصلی
- customer و balance ledger
- sales و payments پایه
- pricing server-side
- packages و VIP
- audit/idempotency پایه
- session/PC
- client heartbeat/agent پایه
- lease/reconnect و manual resume پایه
- WebSocket gateway/presence/command push
- operator desktop پایه
- reservations/queue/group sessions در نسخه‌های اخیر
- customer login/session extend/quick flows در نسخه‌های اخیر
- inventory/FOOD sales در نسخه‌های اخیر
- game catalog و launch authorization در commitهای اخیر

### ناقص / نیازمند بررسی
- customer debt / بدهی
- error-code استاندارد و کامل
- distinction بین Internet و LAN
- RECOVERING semantics و state machine نهایی
- grace period و drift/jitter handling
- security events
- disk-full handling
- backup قبل از migration
- kiosk/lockdown کامل Windows
- game launcher واقعی و process monitoring
- UI کامل client
- WS client/transport کامل و مشخص شدن transport اصلی
- reports / dashboard / alerts / reconciliation
- backup/restore کامل
- installer/build/deployment
- hardening امنیتی، rate limit، token rotation، minimum client version، TLS/at-rest
- concurrency/time/recovery/failure tests
- payroll/shift reconciliation و بخش‌های باقی‌مانده operator
- maintenance/equipment در صورت نبود implementation کامل
- promotions/loyalty و قابلیت‌های باقی‌مانده master spec

## 4) نکات مهمی که باید حتماً راستی‌آزمایی شوند

### A. Payment architecture
در `server/services/payment_service.py` مسیر CARD علاوه بر حالت manual، مسیر automated provider دارد که `start_payment()` و سپس `check_status()` را فراخوانی می‌کند.

سؤال:
- آیا این provider فقط abstraction آینده/غیرفعال است یا واقعاً در base architecture قابل استفاده است؟
- Master design برای نسخه پایه، پرداخت کارت را external POS/manual operator confirmation می‌خواهد و online gateway را جزو client نمی‌خواهد.
- Codespace AI باید با code path و call sites مشخص کند این مسیر چه نقشی دارد و آیا با معماری پایه تضاد عملی ایجاد می‌کند.

### B. Quick customer / recharge
بررسی شود آیا `quick_customer` یا flow مشابه می‌تواند از client مستقیماً balance را تغییر دهد یا خیر.
باید invariant حفظ شود:
Client → request only
Operator → confirm external cash/POS
Server → ledger/audit/activation

### C. Session Extend
بررسی شود extend واقعاً زمان/مدت session را طبق master spec افزایش می‌دهد یا صرفاً marker/state مثل `EXTENDED` ثبت می‌کند.
تأثیر آن بر balance، pricing snapshot، lease، audit و reconnect بررسی شود.

### D. WebSocket vs Agent transport
WebSocket gateway و live command push وجود دارد، اما transport در agent در بخش‌هایی REST-oriented است.
بررسی شود:
- WS برای چه کاری source/primary است؟
- agent در حالت عادی از کدام transport استفاده می‌کند؟
- reconnect/ACK/retry/idempotency بین این دو چگونه تضمین می‌شود؟
- duplicate command یا ACK race چه وضعی دارد؟

### E. Agent local state/security
Agent از `state.json` برای lock/session/ACK/recovery استفاده می‌کند.
بررسی شود:
- چه داده‌ای داخل آن است؟
- آیا قابل دستکاری local user است؟
- server چگونه source of truth باقی می‌ماند؟
- replay/forgery/tampering چه اثری دارد؟

### F. Game catalog / launcher
وجود launch authorization به‌تنهایی به معنی کامل شدن launcher/kiosk نیست.
بررسی شود:
- catalog
- per-PC launch configuration
- secure launch
- process monitoring
- جلوگیری از اجرای برنامه‌های غیرمجاز
- پایان session و kill/cleanup
- recovery پس از crash
- kiosk/Windows lockdown

### G. Financial invariants
برای charge/recharge/payment/refund/adjustment این موارد باید end-to-end قابل اثبات باشند:
- positive amount
- no double credit
- idempotency
- balance_before/after
- operator authorization
- external POS/cash confirmation
- cancellation/refund بدون حذف history
- concurrent operators
- network loss
- server restart
- audit trail
- client cannot mutate balance directly

## 5) اولویت بررسی برای ادامه پروژه

### P0 — معماری و correctness
1. Server source of truth و عدم direct DB access client
2. payment/ledger invariants
3. session/lease/reconnect/manual resume
4. authorization/RBAC
5. idempotency و concurrency
6. state machines و recovery

### P1 — قابلیت‌های عملیاتی اصلی
1. client UI
2. agent ↔ server transport/WS/reconnect
3. kiosk/lockdown
4. game catalog/launcher/process monitor
5. operator flows
6. inventory/cash/shift/reservation completion
7. reports/reconciliation/alerts

### P2 — production readiness
1. backup/restore
2. migrations
3. installer/build
4. logging/observability
5. security hardening
6. failure/recovery tests
7. disk-full/time-drift/network degradation
8. documentation and acceptance checks

## 6) قانون ادامه کار
Codespace AI لازم نیست منتظر ChatGPT بماند. با توجه به معماری و requirement matrix، کوچک‌ترین task امن بعدی را انتخاب و اجرا کند، اما:
- قبل از ادعای «کامل شد» implementation و tests/commit را بررسی کند.
- اگر با یکی از موارد این فایل مخالف است، آن را در `.ai-review/DISCUSSION.md` با evidence مطرح کند.
- اگر موردی قبلاً حل شده، commit/file/function دقیق را ذکر کند و آن مورد را دوباره نسازد.
- اگر موردی فقط planned است، آن را completed حساب نکند.
- قابلیت جدید را فقط برای پر کردن checklist اضافه نکند.
- تست فقط وقتی اجرا شود که برای اثبات/رفع یک سؤال مشخص لازم است.
- Review نباید کار اصلی پروژه را متوقف کند.

## 7) Acceptance معیار کلی
یک قابلیت زمانی «DONE» تلقی شود که implementation، permission/security، persistence، error/recovery، idempotency در صورت نیاز، audit و تست متناسب با اهمیت آن قابل اثبات باشد؛ صرف وجود endpoint/UI یا documentation کافی نیست.

## 8) آخرین نکته
این فایل intentionally یک نقشه بررسی است، نه جایگزین requirement/master spec. اگر بین این فایل و کد/مستندات جدید پروژه اختلاف وجود داشت، Codespace AI باید اختلاف را در Review Board ثبت کند تا مستقل بررسی شود.
