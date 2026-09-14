# Google Analytics 4 Setup for stackcone.com

This document explains the GA4 implementation on stackcone.com and the required admin configuration steps in the Google Analytics UI.

## Implementation Summary

### Analytics Configuration (`/assets/analytics.js`)
- **Measurement ID**: `G-B29M3GX6QM`
- **Page View Tracking**: Enabled via `send_page_view: true`
- **IP Anonymization**: Enabled via `anonymize_ip: true`
- **CTA Click Tracking**: Automatic tracking of primary CTAs, contact links, mailto, and tel links

### Custom Events Tracked

1. **`generate_lead`** (Contact Form)
   - Fires on successful contact form submission (`/contact/`)
   - Parameters: `page_location`, `page_path`, `form_id`, `event_category`, `event_label`, `value`

2. **`page_not_found`** (404 Page)
   - Fires when the 404 page loads
   - Parameters: `page_location`, `page_path`, `page_title`, `event_category`

3. **`cta_click`** (Primary CTAs)
   - Fires when users click primary CTAs, contact links, mailto, or tel links
   - Parameters: `link_url`, `link_text`, `event_category`, `event_label`

## Required Admin Configuration Steps

After deploying these code changes, complete the following steps in the Google Analytics 4 Admin UI:

### 1. Mark Events as Key Events

Navigate to **Admin → Events** (or **Admin → Conversions** in older GA4 UI):

1. Find the `generate_lead` event
   - Click **Mark as key event** (or toggle the conversion switch)
   - This tracks contact form submissions as conversions

2. Find the `page_not_found` event
   - Click **Mark as key event**
   - This helps monitor 404 errors and fix broken links

3. (Optional) Mark `cta_click` as a key event if you want to track engagement with primary CTAs

### 2. Configure Reports Snapshot

Navigate to **Reports → Reports snapshot**:

1. Click **Customize report** in the top right
2. Add cards for:
   - Key events (`generate_lead`, `page_not_found`)
   - User engagement metrics
   - Traffic sources
3. Save the customized snapshot

### 3. (Optional) Exclude Internal Traffic

If you want to exclude traffic from the Bengaluru office:

1. Navigate to **Admin → Data Streams → Web → Configure tag settings → Show more → Define internal traffic**
2. Click **Create**
3. Add rule:
   - **Traffic type**: `Internal Traffic`
   - **IP address**: Enter the office IP address(es)
   - **Condition**: `IP address equals` or `IP address begins with`
4. Save

Then enable the filter:

1. Navigate to **Admin → Data Settings → Data Filters**
2. Find **Internal Traffic** filter
3. Change **Filter State** from `Testing` to `Active`

## Verification

After deploying and configuring:

1. Visit the site in a browser
2. Open **Admin → DebugView** in GA4 (or use the GA Debugger Chrome extension)
3. Navigate to pages and trigger events:
   - Navigate to any page (should see `page_view` events)
   - Click primary CTAs (should see `cta_click` events)
   - Visit a non-existent URL (should see `page_not_found` event)
   - Submit the contact form (should see `generate_lead` event)

## Notes

- The measurement ID is public and visible in page source (this is normal for client-side analytics)
- No GDPR consent banner is implemented; IP anonymization is enabled by default
- Events may take 24-48 hours to appear in standard reports after first deployment
- Real-time reports show events immediately

## Questions or Issues

If key events are still showing zero after 48 hours:
1. Verify the events appear in **Admin → DebugView** or **Reports → Realtime**
2. Check that the events are marked as key events in **Admin → Events**
3. Ensure no GA4 filters are blocking the events
