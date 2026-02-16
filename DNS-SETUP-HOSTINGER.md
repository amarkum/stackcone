# Hostinger DNS setup for GitHub Pages (stackcone.com)

Do these in **Hostinger → stackcone.com → Manage DNS records**.

---

## 1. Fix the A record (apex domain: stackcone.com)

**Current:** `A` `@` → `84.32.84.32` (Hostinger)

**Change it to GitHub Pages:**

- **Edit** the existing `A` record for `@`.
- Set **Points to** to: `185.199.108.153`
- Save.

Then **Add record** 3 more times so you have **four A records** for `@`:

| Type | Name | Points to      | TTL   |
|------|------|----------------|-------|
| A    | @    | 185.199.108.153| 14400 |
| A    | @    | 185.199.109.153| 14400 |
| A    | @    | 185.199.110.153| 14400 |
| A    | @    | 185.199.111.153| 14400 |

(If Hostinger only allows one A for `@`, keep just `185.199.108.153`; it can still work.)

---

## 2. Fix the CNAME for www

**Current:** `CNAME` `www` → `stackcone.com`

**Change it:**

- **Edit** the `CNAME` record where **Name** is `www`.
- Set **Content / Points to** to: `amarkum.github.io`
- TTL: 300 or 14400 is fine. Save.

So you have:

| Type  | Name | Content / Points to  | TTL   |
|-------|------|----------------------|-------|
| CNAME | www  | amarkum.github.io    | 300   |

---

## 3. Leave these as they are (email and security)

Do **not** remove or change:

- All `hostingermail-*` CNAMEs
- `autodiscover` and `autoconfig` CNAMEs
- `MX` records (mx1/mx2.hostinger.com)
- `TXT` for `_dmarc` and `@` (SPF)

---

## 4. After saving DNS

1. In GitHub: **Repo → Settings → Pages → Custom domain**  
   - Enter: `stackcone.com` (or `www.stackcone.com` if you prefer www).  
   - Save. Enable **Enforce HTTPS** when it appears.

2. Wait 5–60 minutes (up to 48 hours in rare cases).

3. Open `https://stackcone.com` (and `https://www.stackcone.com` if you set the CNAME).

---

## Summary

| Record | Name | Points to / Content     | Action   |
|--------|------|-------------------------|----------|
| A      | @    | 185.199.108.153         | Edit/add (add 4 if possible) |
| A      | @    | 185.199.109.153         | Add      |
| A      | @    | 185.199.110.153         | Add      |
| A      | @    | 185.199.111.153         | Add      |
| CNAME  | www  | amarkum.github.io       | Edit     |

Email records: leave unchanged.
