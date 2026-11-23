# Scene rules: structure and behavior only, never looks

Each scene lists what the page must have, how it must behave, and its "Default look" (the most common appearance, which you must differ from on at least one axis).

## saas-site — SaaS / B2B website
Must have: specific value proposition, primary CTA (global: Start free / Sign up; cn: 预约演示 + 免费试用), real product UI near the top, features framed as outcomes, real social proof only, final CTA, footer.
Often: pricing (only if in brief), integrations, security/compliance, FAQ. cn: 解决方案 by 行业 (mega menu), 客户案例 with metrics, floating 在线咨询 rail, 400 phone + QR in footer.
Behaviors: mega menu works with keyboard and touch · floating rail never covers content · specific CTA labels
Default look: neutral + blue, neutral sans, medium radius, soft shadow, product UI

## admin — admin / back-office (中后台)
Must have: sidebar nav (grouped, ≤2 levels, collapsible) + top bar (breadcrumb, search, notifications, user); page header with primary action; filter bar (common visible, more collapsed, 查询/重置); table (selection, sorting, status, row actions, pagination with total); detail page; validated forms.
Behaviors: filters and pagination in URL · batch bar on selection · destructive actions confirm · drawer for medium forms, page for long forms · empty/loading/error on every list · wide tables scroll inside with fixed first/last columns
Default look: neutral + blue, neutral sans, small radius, hairline, compact

## dashboard — analytics dashboard
Must have: KPI row (value, signed change with arrow, period), time range selector, main chart, breakdown table, filters.
Behaviors: range in URL · tabular right-aligned numbers · chart summaries and keyboard tooltips · skeletons sized like content
Default look: neutral + brand, neutral sans, small radius, hairline, compact, data graphics

## fintech — finance, trading, payments
Must have: precise numbers with units and timestamps, change not by color alone, review + confirm before moving money, history.
Behaviors: up/down colors per locale · 万/亿 or K/M with full value accessible · no number animations that delay reading
Default look: neutral + blue, neutral sans, small radius, hairline, compact

## data-screen — data visualization wall (数据大屏)
Must have: fixed canvas (usually 1920×1080, scale to fit, no scroll), header with title + time, 3 columns (KPIs/rankings · hero map or chart · trends/alerts), live-updating data.
Behaviors: labels ≥ 16px at 1920 · auto-rotation pauses on hover · counters animate once · reduced motion honored · sample data marked
Default look: dark, neutral sans + DIN numbers, sharp, layered panels with glowing borders

## ecommerce — store, listing, product detail
Must have: search, categories, product cards (image, name, price, key tag), detail (gallery, price, variants/SKU, stock, delivery, reviews, add to cart / buy), cart.
cn often: banner, 频道 icon grid, 限时秒杀 countdown, coupons, 包邮/满减 tags, 已售, sticky bottom bar (客服, 店铺, 购物车, 加入购物车, 立即购买).
global often: shipping-threshold announcement bar, lifestyle hero, swatches, hover image swap, slide-out cart, returns info.
Behaviors: unavailable variants shown disabled with a label · price + CTA visible without scrolling on mobile detail · bottom bar respects safe area
Default look: cn: neutral + red/orange, vivid promo; global: neutral + black, photography, flat

## mobile-h5 — mobile web / WeChat H5 / mini-program
Must have: 44px nav bar (back + title), grouped cell lists or cards, sticky full-width primary action, bottom tab bar (≤5) if multi-section.
Behaviors: design at 375 · safe-area padding on fixed bars · mini-program: keep top-right capsule area clear · action sheets and toasts instead of desktop modals · inputs 16px · Back never exits a flow unexpectedly
Default look: neutral + green/brand, system sans, medium radius, flat

## content — feed, community, blog, article
Must have: feed or list, detail, author, time, engagement (like/collect/comment/share) or reading aids (TOC, reading time).
Behaviors: images in fixed-ratio boxes · DOM order chronological even in masonry · infinite scroll has an end or load-more and restores position on Back
Default look: white + one accent, neutral sans, medium radius, photography

## gov — government / public service
Must have: search, top-services grid, dated notices, procedure guides (conditions, materials, steps, time limit, location), contacts, accessibility / elderly mode toggle.
Behaviors: elderly mode (larger text, higher contrast, simpler layout) · full keyboard access · PDFs with HTML summary · cn footer: 主办单位, 备案号, 网站标识码
Default look: neutral + official blue or red, neutral sans, small radius, flat, medium

## docs — developer docs / dev tool site
Must have: ⌘K search, left nav tree, content column, on-page TOC, code blocks with copy and language tabs, prev/next, version switcher if versioned.
Behaviors: anchor on every heading · theme toggle + prefers-color-scheme · remembered language tab
Default look: neutral + teal/blue, neutral sans + mono, small radius, hairline

## brand — brand story, campaign, launch, event
Must have: one strong hero idea, story sections, product or event details, clear CTA (buy / register / follow), share.
Behaviors: narrative motion skippable and reduced-motion safe · key info never only inside animation or images
Default look: varies; push expressiveness

## portfolio — personal / studio portfolio
Must have: who + what in the first screen, selected work with outcomes, project pages, contact.
Behaviors: optimized lazy-loaded images · linkable project pages
Default look: neutral sans, airy, type-only or photography
