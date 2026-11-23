# Locale conventions

## cn (mainland China)
- Fonts: don't depend on Google Fonts. System stack: `-apple-system, BlinkMacSystemFont, "PingFang SC", "HarmonyOS Sans SC", "Microsoft YaHei", "Noto Sans SC", sans-serif`. For display or serif personality, self-host subsetted 思源黑体 / 思源宋体 or other licensed fonts. Numbers: `"DIN Alternate", Roboto, sans-serif` + `tabular-nums`.
- Typography: Chinese bold at 500–600 (not 800+); no italics on Chinese; space between Chinese and Latin/numbers (`使用 API 接入`); line-height 1.6–1.8.
- Color meaning: red = celebration / promotion / price; finance: red up (涨), green down (跌).
- Formats: `2026年10月25日` or `2026-10-25`; `¥1,299.00`; 万/亿; phone `138 0000 0000`.
- Auth: 手机号 + 短信验证码 first, 微信扫码 second, password third; 隐私政策 / 用户协议 checkbox unchecked by default.
- Footer: ICP 备案号 link (+ 公安备案 if applicable), company name, service phone, WeChat QR.
- Expectations: 在线客服 entry on marketing sites; QR codes for app / 公众号 / 小程序.

## global
- Fonts: web fonts fine; system fallback.
- Color: green up, red down/danger.
- Auth: email + password / magic link / SSO (Google, Microsoft, GitHub).
- Footer: legal links, cookie preferences where required, status page for SaaS.
- Copy short and direct.
