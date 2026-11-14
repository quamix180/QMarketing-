# Integration Register

Status labels: **Proposed** means not connected or verified. **Requires authorization** means account/API permission and credentials are needed. No live integration is claimed by this document.

| System | Purpose | Status / gate |
|---|---|---|
| LinkedIn | Organization/page content | Proposed; API product and organization permissions must be verified |
| Instagram | Professional account content | Proposed; Meta account linkage and required permissions |
| Facebook | Page content | Proposed; Meta app review and page permissions |
| YouTube | Video uploads and metadata | Proposed; OAuth, API quota and channel authorization |
| X | Posts and media | Proposed; API access tier, permissions and quota |
| TikTok | Video publishing | Proposed; Content Posting API eligibility, app review and account authorization |
| QUAMIX.News / website | Editorial publishing | Proposed; identify actual CMS and authorization |
| CRM (HubSpot or existing QUAMIX CRM) | Lead records and pipeline | Proposed; audit existing system before selecting |
| n8n / Make / Zapier | Workflow automation | Optional evaluation; do not purchase until architecture and costs reviewed |
| Supabase / PostgreSQL | Data storage | Proposed; prefer existing approved QUAMIX database if available |
| PostHog / Google Analytics | Product and website analytics | Proposed; verify current property, consent and data quality |
| Canva | Brand templates and creative workflows | Proposed; account and brand-kit access required |
| HeyGen / text-to-speech | Presenter video and narration | Proposed; paid usage and voice/likeness rights require approval |
| Image/video generation | Original creative assets | Proposed; model/tool, licensing and cost review |

## Integration rules
- Use official APIs or explicitly authorized providers.
- Never scrape or automate UI in violation of platform terms.
- Keep tokens in a secrets manager, never Git.
- Use least-privilege scopes and per-account identities.
- Record consent, purpose, retention and source for CRM data.
- Respect rate limits, quotas, deletion requests and platform policy.
- Test in sandbox/staging before production.
- Record token expiry/revocation and provide a disable switch.

## Activation sequence
1. Audit existing accounts, CMS, CRM and analytics.
2. Verify platform API eligibility and account ownership.
3. Obtain explicit account authorization.
4. Build/test a read-only or draft-only adapter first.
5. Test approval enforcement and provider response handling.
6. Enable publication only after Founder approval and staging acceptance.
